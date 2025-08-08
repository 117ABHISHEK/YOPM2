from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import math

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

        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return render_template('register.html', form_data=request.form)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cur.fetchone()
        if user:
            if user['username'] == username:
                flash("Username already exists!", 'danger')
            elif user['email'] == email:
                flash("Email already registered!", 'danger')
            cur.close()
            return render_template('register.html', form_data=request.form)
        cur.close()

        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                    (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please login.", 'success')
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
            flash("Login successful!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", 'info')
    return redirect(url_for('index'))

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please login first.", 'warning')
        return redirect(url_for('login'))

    page = request.args.get('page', 1, type=int)
    per_page = 10

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(id) FROM learning_entries WHERE user_id = %s", (session['uid'],))
    total_entries = cur.fetchone()['COUNT(id)']
    total_pages = math.ceil(total_entries / per_page) if total_entries > 0 else 1

    offset = (page - 1) * per_page
    cur.execute(
        "SELECT * FROM learning_entries WHERE user_id = %s ORDER BY date DESC LIMIT %s OFFSET %s",
        (session['uid'], per_page, offset)
    )
    entries = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', entries=entries, username=session['username'], 
                           page=page, total_pages=total_pages)

def validate_entry_form(form):
    errors = []
    date_str = form.get('date', '').strip()
    title = form.get('title', '').strip()
    content = form.get('content', '').strip()
    time_spent = form.get('time', '').strip()

    if not date_str or not title or not content:
        errors.append(("Date, title, and content are required.", "danger"))

    if date_str:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            errors.append(("Invalid date format. Use YYYY-MM-DD.", "danger"))

    if time_spent:
        try:
            float(time_spent)
        except ValueError:
            errors.append(("Time spent must be a number.", "danger"))

    return errors

# --- Add Entry ---
@app.route('/entry', methods=['GET', 'POST'])
def entry():
    if 'username' not in session:
        flash("Please login first.", 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        errors = validate_entry_form(request.form)
        if errors:
            for error_msg, category in errors:
                flash(error_msg, category)
            return render_template('entry.html', entry=request.form)

        date = request.form.get('date', '').strip()
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        tags = request.form.get('tags', '').strip()
        project = request.form.get('project', '').strip()
        reflection = request.form.get('reflection', '').strip()
        resources = request.form.get('resources', '').strip()
        time_spent_str = request.form.get('time', '').strip()
        time_spent = float(time_spent_str) if time_spent_str else None

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO learning_entries 
            (date, title, content, tags, project, reflection, resources, time_spent, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (date, title, content, tags, project, reflection, resources, time_spent, session['uid']))
        mysql.connection.commit()
        cur.close()

        flash("Learning entry added!", 'success')
        return redirect(url_for('dashboard'))

    return render_template('entry.html', entry=None)

@app.route('/view_entry/<int:id>')
def view_entry(id):
    if 'uid' not in session:
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM learning_entries WHERE id = %s AND user_id = %s",
        (id, session['uid'])
    )
    entry = cur.fetchone()
    cur.close()

    if not entry:
        flash("Entry not found.", 'danger')
        return redirect(url_for('dashboard'))

    return render_template('view_entry.html', entry=entry)

# --- Update Entry ---
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    if 'username' not in session:
        flash("Please login first.", 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        errors = validate_entry_form(request.form)
        if errors:
            for error_msg, category in errors:
                flash(error_msg, category)
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
        time_spent = float(time_spent_str) if time_spent_str else None

        cur.execute("""
            UPDATE learning_entries SET
            date = %s, title = %s, content = %s, tags = %s, project = %s,
            reflection = %s, resources = %s, time_spent = %s
            WHERE id = %s AND user_id = %s
        """, (date, title, content, tags, project, reflection, resources, time_spent, id, session['uid']))
        mysql.connection.commit()
        cur.close()

        flash("Entry updated!", 'success')
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM learning_entries WHERE id = %s AND user_id = %s", (id, session['uid']))
    entry = cur.fetchone()
    cur.close()

    if not entry: 
        flash("Entry not found or you don't have permission.", 'danger')
        return redirect(url_for('dashboard'))

    return render_template('entry.html', entry=entry)

# --- Delete Entry ---
@app.route('/delete/<int:id>')
def delete(id):
    if 'username' not in session:
        flash("Please login first.", 'warning')
        return redirect(url_for('login'))

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM learning_entries WHERE id = %s AND user_id = %s", (id, session['uid']))
    mysql.connection.commit()
    cur.close()

    flash("Entry deleted!", 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
