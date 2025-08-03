from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)

# --- Configuration ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_learnlog'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'super secret key'

mysql = MySQL(app)

# --- Home ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        errors = []

        if password != confirm_password:
            errors.append(("Passwords do not match!", "danger"))

        if not errors:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            user = cur.fetchone()
            if user:
                if user['username'] == username:
                    errors.append(('Username already exists!', "danger"))
                if user['email'] == email:
                    errors.append(('Email address already registered!', "danger"))
            cur.close()

        if errors:
            for error, category in errors:
                flash(error, category)
            return render_template('register.html', form_data=request.form)

        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form_data=None)


# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, username))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['uid'] = user['id']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM learning_entries where user_id = %s ORDER BY date DESC", (session['uid'],))
    entries = cur.fetchall()
    print(entries) 
    return render_template('dashboard.html', entries=entries, username=session['username'])

def validate_entry_form(form):
    """Helper function to validate the learning entry form."""
    errors = []
    date_str = form.get('date', '').strip()
    title = form.get('title', '').strip()
    content = form.get('content', '').strip()
    time_spent = form.get('time', '').strip()

    if not date_str or not title or not content:
        errors.append(('Date, title, and content are required fields.', 'danger'))

    if date_str:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            errors.append(('Invalid date format. Please use YYYY-MM-DD.', 'danger'))

    if time_spent and not time_spent.isdigit():
        errors.append(('Time spent must be a number (e.g., 60 for 60 minutes).', 'danger'))

    return errors

# --- Add Entry ---
@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        errors = validate_entry_form(request.form)
        if errors:
            for error, category in errors:
                flash(error, category)
            return render_template('entry.html', entry=request.form)

        date = request.form.get('date', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        tags = request.form.get('tags', '').strip()
        project = request.form.get('project', '').strip()
        reflection = request.form.get('reflection', '').strip()
        resources = request.form.get('resources', '').strip()
        time_spent_str = request.form.get('time', '').strip()
        time_spent = int(time_spent_str) if time_spent_str.isdigit() else None

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO learning_entries 
            (date, title, content, tags, project, reflection, resources, time_spent, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (date, title, content, tags, project, reflection, resources, time_spent, session['uid'])
        )
        mysql.connection.commit()
        cur.close()

        flash('Learning entry added!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('entry.html', entry=None)

@app.route('/view_entry/<int:id>')
def view_entry(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM learning_entries WHERE id = %s AND user_id = %s", (id, session['uid']))
    entry = cur.fetchone()
    cur.close()

    if not entry:
        flash('Entry not found.')
        return redirect(url_for('dashboard'))
    else:
        return render_template('view_entry.html', entry=entry)
 
# --- Update Entry ---
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        errors = validate_entry_form(request.form)
        if errors:
            for error, category in errors:
                flash(error, category)
            form_data = request.form.to_dict()
            form_data['id'] = id
            cur.close()
            return render_template('entry.html', entry=form_data)

        date = request.form.get('date', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        tags = request.form.get('tags', '').strip()
        project = request.form.get('project', '').strip()
        reflection = request.form.get('reflection', '').strip()
        resources = request.form.get('resources', '').strip()
        time_spent_str = request.form.get('time', '').strip()
        time_spent = int(time_spent_str) if time_spent_str.isdigit() else None

        cur.execute("""
            UPDATE learning_entries SET
            date = %s, title = %s, content = %s, tags = %s, project = %s,
            reflection = %s, resources = %s, time_spent = %s
            WHERE id = %s AND user_id = %s
            """,
            (date, title, content, tags, project, reflection, resources, time_spent, id, session['uid'])
        )
        mysql.connection.commit()
        cur.close()

        flash('Entry updated!', 'success')
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM learning_entries WHERE id = %s AND user_id = %s", (id, session['uid']))
    entry = cur.fetchone()
    cur.close()

    if not entry: 
        flash('Entry not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('entry.html', entry=entry)

# --- Delete Entry ---
@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM learning_entries WHERE id = %s AND user_id = %s", (id, session['uid']))
    mysql.connection.commit()
    cur.close()

    flash('Entry deleted!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
