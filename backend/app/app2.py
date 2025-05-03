from app.extensions import db
from models import User, AuthToken  # Импортируем ваши модели

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Создаем таблицы в базе данных
with app.app_context():
    db.create_all()