# app.py
from flask import Flask, render_template, request, redirect, url_for
from models import db, Task
import sqlite3
import os
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("Tables created.")

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')

    # Создаем новую задачу и добавляем ее в базу данных
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()

    # Перенаправляем на главную страницу после добавления задачи
    return redirect(url_for('index'))

@app.route('/check_db')
def check_db():
    connection = sqlite3.connect('tasks.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM task")
    tasks = cursor.fetchall()
    connection.close()

    return "<br>".join([f"Title: {task[1]}, Description: {task[2]}" for task in tasks])

if __name__ == '__main__':
    app.run(debug=True)

