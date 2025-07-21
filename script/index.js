// Express.js and SQLite setup for LearnLog backend
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bodyParser = require('body-parser');
const session = require('express-session');

const app = express();
const PORT = 3000;

// SQLite DB setup
const db = new sqlite3.Database('./learnlog.db', (err) => {
  if (err) {
    console.error('Could not connect to database', err);
  } else {
    console.log('Connected to SQLite database');
  }
});

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )`);
});

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(session({
  secret: 'learnlog_secret',
  resave: false,
  saveUninitialized: true,
}));

// Serve static files
app.use('/style', express.static(path.join(__dirname, '../style')));
app.use('/templates', express.static(path.join(__dirname, '../templates')));
app.use(express.static(path.join(__dirname, '../templates'))); // Serve templates from root

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../templates/index.html'));
});

// --- REST API: Register ---
app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }
  db.run(
    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
    [username, email, password],
    function (err) {
      if (err) {
        if (err.message.includes('UNIQUE')) {
          return res.status(409).json({ error: 'Username or email already exists.' });
        }
        return res.status(500).json({ error: 'Database error.' });
      }
      req.session.userId = this.lastID;
      res.json({ success: true, userId: this.lastID });
    }
  );
});

// --- REST API: Login ---
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }
  db.get(
    'SELECT * FROM users WHERE username = ? AND password = ?',
    [username, password],
    (err, user) => {
      if (err) return res.status(500).json({ error: 'Database error.' });
      if (!user) return res.status(401).json({ error: 'Invalid credentials.' });
      req.session.userId = user.id;
      res.json({ success: true, userId: user.id });
    }
  );
});

// --- REST API: Logout ---
app.post('/api/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

// --- REST API: Session Check ---
app.get('/api/session', (req, res) => {
  if (req.session.userId) {
    db.get('SELECT id, username, email FROM users WHERE id = ?', [req.session.userId], (err, user) => {
      if (err || !user) return res.status(401).json({ loggedIn: false });
      res.json({ loggedIn: true, user });
    });
  } else {
    res.json({ loggedIn: false });
  }
});

// Export app for testing or further extension
module.exports = app;

// Start server if run directly
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}
