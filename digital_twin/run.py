from app import create_app
import os

if __name__ == '__main__':
    app, socketio = create_app()
    
    # Run the application
    socketio.run(app, 
                host='0.0.0.0', 
                port=5000, 
                debug=True,
                allow_unsafe_werkzeug=True)