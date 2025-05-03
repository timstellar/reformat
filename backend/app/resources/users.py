from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.schemas.user import user_schema, users_schema
from app.utils.errors import not_found
from app.utils.auth import admin_required

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    if user_id != current_user_id and not User.query.get(current_user_id).is_admin:
        return unauthorized("Not authorized to view this user")
    
    user = User.query.get(user_id)
    if not user:
        return not_found('User not found')
    return jsonify(user_schema.dump(user))

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return jsonify(user_schema.dump(user))