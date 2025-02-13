import eventlet
eventlet.monkey_patch()  # ✅ MUST BE FIRST

from flask import Flask, render_template
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///messages.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and WebSocket server
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='eventlet')

# Message Model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(500), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Load the chat page with previous messages."""
    messages = Message.query.all()
    return render_template('index.html', messages=messages)

@socketio.on('message')
def handle_message(msg):
    """Handle incoming messages and store them in the database."""
    print(f'Received message: {msg}')
    username = "User"  # Default username
    new_message = Message(username=username, text=msg)
    db.session.add(new_message)
    db.session.commit()
    send(f"{username}: {msg}", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
