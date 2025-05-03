from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
from app.extensions import db
from datetime import datetime, timedelta

def create_token(user_id):
    """Create and store a new auth token"""
    expires = timedelta(hours=1)
    token = create_access_token(identity=user_id, expires_delta=expires)
    
    auth_token = AuthToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.utcnow() + expires
    )
    db.session.add(auth_token)
    db.session.commit()
    return token

def token_required(fn):
    """Verify token is valid and active"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        token = get_jwt_token()
        user = AuthToken.query.filter_by(token=token, is_active=True).first()
        
        if not user or user.expires_at < datetime.utcnow():
            return jsonify({"error": "Invalid or expired token"}), 401
            
        g.current_user = user.user
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    """Verify user is admin"""
    @wraps(fn)
    @token_required
    def wrapper(*args, **kwargs):
        if not g.current_user.is_admin:
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

def get_jwt_token():
    """Extract JWT token from request header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]