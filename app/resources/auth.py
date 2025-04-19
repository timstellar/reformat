from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from app.schemas.user import user_schema
from app.utils.errors import bad_request, unauthorized
from app.extensions import db

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    required_fields = ['username', 'password', 'email']
    if not all(field in data for field in required_fields):
        return bad_request('Missing required fields')
    
    if User.query.filter_by(username=data['username']).first():
        return bad_request('Username already exists', 409)
    
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Email already exists', 409)
    
    user = User(
        username=data['username'],
        email=data['email'],
        is_admin=data.get('is_admin', False)
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': user_schema.dump(user)
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(data)
    if not data or not data.get('username') or not data.get('password'):
        return bad_request('Username and password required')
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return unauthorized('Invalid credentials')
    
    if not user.is_active:
        return unauthorized('Account disabled', 403)
    
    access_token = create_access_token(identity=user.id)
    return jsonify({
        'access_token': access_token,
        'user': user_schema.dump(user)
    })

@bp.route('/tokens', methods=['GET'])
@jwt_required()
def list_tokens():
    current_user_id = get_jwt_identity()
    tokens = AuthToken.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        'id': t.id,
        'created_at': t.created_at.isoformat(),
        'expires_at': t.expires_at.isoformat(),
        'is_active': t.is_active
    } for t in tokens])

@bp.route('/revoke/<int:token_id>', methods=['POST'])
@jwt_required()
def revoke_token(token_id):
    current_user_id = get_jwt_identity()
    token = AuthToken.query.filter_by(id=token_id, user_id=current_user_id).first()
    
    if not token:
        return not_found('Token not found')
    
    token.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'Token revoked'})