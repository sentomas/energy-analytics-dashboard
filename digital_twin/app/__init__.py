from flask import Flask
from flask_socketio import SocketIO
from pymongo import MongoClient
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # MongoDB connection
    app.config['MONGO_URI'] = "mongodb://petrus:petrusConnect@10.20.30.130:27017/?authMechanism=DEFAULT"
    
    # Initialize SocketIO for real-time updates
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app, socketio