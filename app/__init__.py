from flask import Flask
from app.config import Config
from app.extensions import db, ma, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    # ... existing config code ...
    
    # Register blueprints
    from app.resources import auth, users, json_parser
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(json_parser.bp)
    
    return app