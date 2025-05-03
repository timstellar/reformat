import os
import secrets # Для генерации безопасных токенов
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash # Для хеширования паролей

# --- 1. Настройка Flask приложения ---
# Это нужно для создания контекста приложения, чтобы SQLAlchemy работала
app = Flask(__name__)

# --- 2. Настройка Базы Данных ---
# ВАЖНО: Путь должен быть ТОЧНО ТАКИМ ЖЕ, как в initialize_db.py и вашем основном app.py
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'my_app_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Инициализация SQLAlchemy ---
db = SQLAlchemy(app)

# --- 4. Определение МОДЕЛЕЙ ---
# Модели должны быть определены здесь точно так же, как они определены
# в других ваших файлах (initialize_db.py, app.py), чтобы SQLAlchemy
# понимало, с какими структурами данных оно работает.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    tokens = db.relationship('AuthToken', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<AuthToken {self.token[:10]}...>'

# --- 5. Функция для добавления данных ---
def add_seed_data():
    print("Начинаем добавление начальных данных...")

    # --- Данные для добавления ---
    users_to_add = [
        {'username': 'admin_user', 'email': 'admin@example.com', 'password': 'AdminPassword123', 'is_admin': True},
        {'username': 'test_user', 'email': 'test@example.com', 'password': 'TestPassword456', 'is_admin': False},
        {'username': 'another_user', 'email': 'another@sample.org', 'password': 'AnotherSecurePwd', 'is_admin': False},
    ]

    # Используем контекст приложения для работы с БД
    with app.app_context():
        for user_data in users_to_add:
            try:
                # Проверяем, не существует ли уже пользователь с таким username или email
                existing_user = db.session.execute(
                    db.select(User).filter(
                        (User.username == user_data['username']) | (User.email == user_data['email'])
                    )
                ).scalar_one_or_none()

                if existing_user:
                    print(f"Пользователь '{user_data['username']}' или email '{user_data['email']}' уже существует. Пропускаем.")
                    continue # Переходим к следующему пользователю в цикле

                # Хешируем пароль
                hashed_password = generate_password_hash(user_data['password'])

                # Создаем объект пользователя
                new_user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=hashed_password,
                    is_active=True,
                    is_admin=user_data['is_admin']
                )

                # Добавляем пользователя в сессию
                db.session.add(new_user)
                # ВАЖНО: Нужно закоммитить здесь, чтобы получить new_user.id для токена
                # Либо можно добавить все и закоммитить в конце, но тогда сложнее сразу создать токен
                # Мы будем коммитить после добавления пользователя И его токена
                print(f"Подготовка к добавлению пользователя: {new_user.username}")

                # Создаем токен для нового пользователя (для примера)
                token_value = secrets.token_urlsafe(40) # Генерируем случайный токен
                expires = datetime.utcnow() + timedelta(days=30) # Токен действителен 30 дней

                new_token = AuthToken(
                    token=token_value,
                    user=new_user, # SQLAlchemy само подставит user_id после коммита пользователя
                    expires_at=expires,
                    is_active=True
                )
                db.session.add(new_token)
                print(f"  Подготовка к добавлению токена для {new_user.username}")

                # Сохраняем пользователя и токен в базе данных
                db.session.commit()
                print(f"Пользователь '{new_user.username}' и его токен успешно добавлены (ID пользователя: {new_user.id}).")

            except Exception as e:
                # Если произошла ошибка (например, нарушение уникальности), откатываем изменения
                db.session.rollback()
                print(f"Ошибка при добавлении пользователя '{user_data['username']}': {e}")

        print("-" * 20)
        print("Проверка существующих пользователей в БД:")
        all_users = db.session.execute(db.select(User)).scalars().all()
        if all_users:
            for user in all_users:
                print(f" - ID: {user.id}, Имя: {user.username}, Email: {user.email}, Админ: {user.is_admin}")
        else:
            print("В базе данных нет пользователей.")
        print("-" * 20)


# --- 6. Запуск функции добавления данных ---
if __name__ == '__main__':
    add_seed_data()
    print("Скрипт 'seed_data.py' завершил работу.")

# --- (Конец кода в seed_data.py) ---