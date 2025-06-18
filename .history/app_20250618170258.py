import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key-please-change')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)

# Todo Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Todo {self.title}>'

# Create database tables
with app.app_context():
    db.create_all()

def send_email_notification(todo):
    """Send email notification when a new todo is added"""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv('SMTP_USERNAME')
        msg['To'] = os.getenv('SMTP_USERNAME')  # Sending to self for demo
        msg['Subject'] = f"New Todo Added: {todo.title}"

        body = f"""
        A new todo item has been added:
        
        Title: {todo.title}
        Description: {todo.description}
        Created at: {todo.created_at}
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587)))
        server.starttls()
        server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def index():
    """Display all todo items"""
    todos = Todo.query.order_by(Todo.created_at.desc()).all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['GET', 'POST'])
def add():
    """Add a new todo item"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash('Title is required!', 'error')
            return redirect(url_for('add'))

        todo = Todo(title=title, description=description)
        db.session.add(todo)
        db.session.commit()

        # Send email notification
        send_email_notification(todo)

        flash('Todo added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    """Delete a todo item"""
    todo = Todo.query.get_or_404(id)
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/toggle/<int:id>')
def toggle(id):
    """Toggle completion status of a todo item"""
    todo = Todo.query.get_or_404(id)
    todo.completed = not todo.completed
    db.session.commit()
    
    status = "completed" if todo.completed else "uncompleted"
    flash(f'Todo marked as {status}!', 'success')
    return redirect(url_for('index'))

@app.route('/status')
def status():
    """Return API status"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True) 