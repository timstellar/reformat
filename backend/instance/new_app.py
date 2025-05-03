import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- 1. Настройка Flask приложения ---
# Создаем экземпляр Flask. Он нужен для контекста, даже если мы не делаем веб-сервер прямо сейчас.
app = Flask(__name__)

# --- 2. Настройка ОДНОЙ Базы Данных ---
# Указываем путь к НАШЕЙ ЕДИНОЙ базе данных SQLite.
# Flask-SQLAlchemy создаст этот файл, если его нет.
# Имя файла будет 'my_app_database.db' в той же папке, где скрипт.
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'my_app_database.db')
# Отключаем необязательное отслеживание (рекомендовано)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Инициализация SQLAlchemy ---
# Создаем ОБЪЕКТ `db`, который будет управлять НАШЕЙ ЕДИНОЙ базой данных.
# Мы связываем его с нашим `app`.
db = SQLAlchemy(app)


# --- 4. Определение МОДЕЛЕЙ (структуры таблиц) ---
# ВАЖНО: Обе модели должны наследоваться от `db.Model`, используя ОДИН И ТОТ ЖЕ объект `db`.
# Это говорит SQLAlchemy, что обе таблицы должны быть в базе данных, управляемой этим `db`.

class User(db.Model):
    # Имя таблицы будет автоматически 'user' (из имени класса в нижнем регистре)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    # Связь с таблицей 'auth_token'
    tokens = db.relationship('AuthToken', backref='user', lazy=True)

    def __repr__(self):
        # Удобное представление объекта при печати
        return f'<User {self.username}>'


class AuthToken(db.Model):
    # Имя таблицы будет автоматически 'auth_token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    # Внешний ключ, связывающий ЭТУ таблицу с таблицей 'user'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<AuthToken {self.token[:10]}...>'


# --- 5. Создание ВСЕХ таблиц в ОДНОЙ базе данных ---
# Используем контекст приложения Flask.
with app.app_context():
    print(f"Подготовка к созданию таблиц в базе данных: {app.config['SQLALCHEMY_DATABASE_URI']}")
    # КЛЮЧЕВАЯ КОМАНДА: db.create_all()
    # Эта команда смотрит на ВСЕ классы, унаследованные от `db.Model` (в нашем случае User и AuthToken),
    # и создает соответствующие таблицы (user, auth_token) в ОДНОЙ базе данных,
    # указанной в `SQLALCHEMY_DATABASE_URI`.
    # Если таблицы уже существуют, ничего не произойдет.
    db.create_all()
    print("Таблицы 'user' и 'auth_token' успешно созданы (или уже существовали) в ОДНОЙ базе данных.")

print("Скрипт 'initialize_db.py' завершил работу.")

# --- (Конец кода в initialize_db.py) ---
