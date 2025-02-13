import eventlet
from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
import os

# Monkey-patch for WebSockets support
eventlet.monkey_patch()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='eventlet')

# Define Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"<Message {self.username}: {self.text}>"

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    messages = Message.query.all()
    return render_template('index.html', messages=messages)

@socketio.on('message')
def handle_message(msg):
    print(f'Received message: {msg}')
    
    username = "User"  # Change this if using authentication
    new_message = Message(username=username, text=msg)
    db.session.add(new_message)
    db.session.commit()

    send(msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
