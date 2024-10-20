import os
import sqlite3
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import db, User, Task
from forms import LoginForm, RegistrationForm, PasswordRecoveryForm, TaskForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already exists. Please use a different email.', 'danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    else:
        print("Form validation failed or GET request")
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/recover', methods=['GET', 'POST'])
def recover():
    form = PasswordRecoveryForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Password recovery instructions have been sent to your email.', 'info')
        else:
            flash('Email not found.', 'danger')
    return render_template('recover.html', form=form)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('index'))
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', form=form, tasks=tasks)

@app.route('/check_db')
def check_db():
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()
        
        # Check if the 'tasks' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task';")
        table_exists = cursor.fetchone()
        
        if table_exists:
            return "Table 'tasks' exists."
        else:
            return "Table 'tasks' does not exist."
        
        # Close the connection
        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
        return f"SQLite error: {e}"

if __name__ == "__main__":
    with app.app_context():
        print('Creating database...')
        db.create_all()
        print('Database created...')
    app.run(debug=True)
