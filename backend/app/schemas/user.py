from app.extensions import ma
from app.models.user import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
        load_only = ('password',)  # Only for loading, not dumping

    # Add any custom fields if needed
    links = ma.Hyperlinks({
        'self': ma.URLFor('users.get_user', id='<id>'),
        'collection': ma.URLFor('users.get_users')
    })

# Create instances of the schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)