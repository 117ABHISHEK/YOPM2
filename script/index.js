// File: app.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
const db = new sqlite3.Database('./learnlog.db', (err) => {
  if (err) console.error('Could not connect to database', err);
  else console.log('Connected to SQLite database on localhost:5173');
});

// Create users table
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
  )`);
});

// Middleware
app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use('/style', express.static(path.join(__dirname, 'style')));
app.use('/script', express.static(path.join(__dirname, 'script')));
app.use(express.static(path.join(__dirname, 'templates')));

// JWT Authentication Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) return res.status(401).send('Access Denied: No Token Provided');

  jwt.verify(token, 'AmpQZGf4ex', (err, user) => {
    if (err) return res.status(403).send('Invalid Token');
    req.user = user;
    next();
  });
};

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates/index.html'));
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates/login.html'));
});

app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates/register.html'));
});

// Register
app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  bcrypt.hash(password, 10, (err, hashedPassword) => {
    if (err) return res.status(500).json({ error: 'Password hashing failed' });

    db.run(
      'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
      [username, email, hashedPassword],
      function (err) {
        if (err) {
          if (err.message.includes('UNIQUE')) {
            return res.status(409).json({ error: 'Username or email already exists.' });
          }
          return res.status(500).json({ error: 'Database error.' });
        }
        res.json({ success: true, userId: this.lastID });
      }
    );
  });
});

// Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'All fields are required.' });
  }

  db.get('SELECT * FROM users WHERE username = ?', [username], (err, user) => {
    if (err) return res.status(500).json({ error: 'Database error.' });
    if (!user) return res.status(401).json({ error: 'Invalid credentials.' });

    bcrypt.compare(password, user.password, (err, result) => {
      if (result) {
        const token = jwt.sign({ userId: user.id }, 'AmpQZGf4ex', { expiresIn: '1h' });
        res.json({ success: true, token });
      } else {
        res.status(401).json({ error: 'Invalid credentials.' });
      }
    });
  });
});

// Session Check (via token)
app.get('/api/session', authenticateToken, (req, res) => {
  db.get('SELECT id, username, email FROM users WHERE id = ?', [req.user.userId], (err, user) => {
    if (err || !user) return res.status(401).json({ loggedIn: false });
    res.json({ loggedIn: true, user });
  });
});

module.exports = app;
