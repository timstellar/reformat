import os
from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func  # Импортируем func для использования функций SQL (например, COUNT)

# --- 1. Настройка Flask приложения ---
# Необходимо для контекста, чтобы SQLAlchemy знала, с какой БД работать
app = Flask(__name__)

# --- 2. Настройка Базы Данных ---
# Указываем путь к ТОМУ ЖЕ файлу базы данных, что и раньше
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'my_app_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Инициализация SQLAlchemy ---
db = SQLAlchemy(app)


# --- 4. Определение МОДЕЛЕЙ ---
# КРАЙНЕ ВАЖНО: Модели должны быть определены здесь ТОЧНО ТАК ЖЕ,
# как и в скриптах создания и записи данных. SQLAlchemy использует их
# для понимания структуры таблиц и преобразования строк БД в объекты Python.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Мы его не будем выводить, но он должен быть в модели
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    tokens = db.relationship('AuthToken', backref='user', lazy=True)  # Связь важна для запроса токенов

    def __repr__(self):
        return f'<User ID:{self.id} Name:{self.username}>'


class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        # Показываем связь с пользователем через backref 'user'
        user_info = f"User ID:{self.user.id}" if self.user else "No User Linked"
        return f'<Token ID:{self.id} Value:{self.token[:10]}... For:{user_info}>'


# --- 5. Функция для выполнения запросов ---
def query_database_data():
    print("Начинаем запрашивать данные из базы...")

    # Используем контекст приложения для работы с БД
    with app.app_context():
        try:
            print("\n--- 1. Получение ВСЕХ пользователей (отсортировано по имени) ---")
            # Современный способ запроса с Flask-SQLAlchemy 3+
            all_users_query = db.select(User).order_by(User.username)
            all_users = db.session.execute(all_users_query).scalars().all()  # scalars() для объектов, all() для списка

            if all_users:
                for user in all_users:
                    print(f"  ID: {user.id}, Имя: {user.username}, Email: {user.email}, Админ: {user.is_admin}")
            else:
                print("  В базе данных нет пользователей.")

            print("\n--- 2. Получение пользователя по ID (например, ID=2) ---")
            user_id_to_find = 2
            user_by_id = db.session.execute(
                db.select(User).filter_by(id=user_id_to_find)
            ).scalar_one_or_none()  # scalar_one_or_none() ожидает 0 или 1 результат

            if user_by_id:
                print(f"  Найден пользователь: ID={user_by_id.id}, Имя={user_by_id.username}")
                # --- 2а. Получение токенов для ЭТОГО пользователя ---
                print(f"    Токены для пользователя '{user_by_id.username}':")
                if user_by_id.tokens:  # Доступ к связанным токенам через user.tokens
                    for token in user_by_id.tokens:
                        expires_str = token.expires_at.strftime('%Y-%m-%d %H:%M') if token.expires_at else 'N/A'
                        print(
                            f"      - Token ID: {token.id}, Value: {token.token[:15]}..., Active: {token.is_active}, Expires: {expires_str}")
                else:
                    print("      У этого пользователя нет токенов.")
            else:
                print(f"  Пользователь с ID={user_id_to_find} не найден.")

            print("\n--- 3. Получение пользователя по имени (например, username='admin_user') ---")
            username_to_find = 'admin_user'
            user_by_name = db.session.execute(
                db.select(User).filter_by(username=username_to_find)
            ).scalar_one_or_none()

            if user_by_name:
                print(
                    f"  Найден пользователь: ID={user_by_name.id}, Имя={user_by_name.username}, Email={user_by_name.email}")
            else:
                print(f"  Пользователь с именем '{username_to_find}' не найден.")

            print("\n--- 4. Получение только АДМИНИСТРАТОРОВ ---")
            admin_users_query = db.select(User).filter_by(is_admin=True)
            admin_users = db.session.execute(admin_users_query).scalars().all()

            if admin_users:
                print("  Найденные администраторы:")
                for admin in admin_users:
                    print(f"    - {admin.username} (ID: {admin.id})")
            else:
                print("  Администраторы не найдены.")

            print("\n--- 5. Получение всех АКТИВНЫХ токенов ---")
            active_tokens_query = db.select(AuthToken).filter_by(is_active=True)
            active_tokens = db.session.execute(active_tokens_query).scalars().all()

            if active_tokens:
                print("  Найденные активные токены:")
                for token in active_tokens:
                    # Используем __repr__ модели AuthToken, который мы улучшили
                    print(f"    - {token}")
            else:
                print("  Активные токены не найдены.")

            print("\n--- 6. Подсчет общего количества пользователей ---")
            user_count_query = db.select(func.count(User.id))  # func.count() для SQL COUNT
            total_users = db.session.execute(
                user_count_query).scalar_one()  # scalar_one() для получения одного значения

            print(f"  Всего пользователей в базе: {total_users}")

            print("\n--- 7. Подсчет общего количества токенов ---")
            token_count_query = db.select(func.count(AuthToken.id))
            total_tokens = db.session.execute(token_count_query).scalar_one()

            print(f"  Всего токенов в базе: {total_tokens}")


        except Exception as e:
            print(f"\n!!! Произошла ошибка при запросе данных: {e}")


# --- 6. Запуск функции запроса данных ---
if __name__ == '__main__':
    query_database_data()
    print("\nСкрипт 'query_data.py' завершил работу.")

# --- (Конец кода в query_data.py) ---
