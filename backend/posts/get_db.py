import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- 1. Настройка Flask приложения ---
# Создаем экземпляр Flask. Он нужен для контекста работы SQLAlchemy.
app = Flask(__name__)

# --- 2. Настройка Базы Данных ---
# ВАЖНО: Указываем ТОЧНО ТОТ ЖЕ путь к файлу базы данных,
# который использовался при ее создании (файл address_posts.db).
basedir = os.path.abspath(os.path.dirname(__file__))
db_filename = 'address_posts.db'
db_path = os.path.join(basedir, db_filename)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Работаем с базой данных: {db_path}")

# --- 3. Инициализация SQLAlchemy ---
# Создаем объект 'db', связанный с нашим приложением и базой данных.
db = SQLAlchemy(app)

# --- 4. Определение МОДЕЛИ Posts ---
# ОБЯЗАТЕЛЬНО: Определение модели должно быть точно таким же,
# как в скрипте создания БД (create_address_db.py).
# SQLAlchemy использует это определение, чтобы понимать, как работать с данными.
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Указываем наше поле relative_address
    relative_address = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        # Удобное представление объекта
        return f'<Post ID: {self.id}, Address: {self.relative_address[:50]}...>'

# --- 5. Функция для добавления данных ---
def add_some_addresses():
    print("Начинаем добавление относительных адресов в таблицу 'posts'...")

    # Список относительных адресов для добавления
    addresses_to_add = [
        "/images/logo.png",
        "/articles/how-to-use-flask",
        "/static/css/main.css",
        "/products/item/123",
        "/user/profile/settings",
        "/api/v1/data"
    ]

    # Используем контекст приложения Flask для работы с сессией БД
    with app.app_context():
        try:
            print("Создаем объекты Posts для каждого адреса:")
            # Список для хранения созданных объектов (не обязательно, но удобно для вывода)
            posts_objects = []
            for address in addresses_to_add:
                # Шаг 1: Создаем экземпляр (объект) модели Posts для каждого адреса
                # Передаем значение в конструктор через имя поля: relative_address=address
                new_post = Posts(relative_address=address)
                posts_objects.append(new_post)
                print(f"  - Подготовлен пост с адресом: {address}")

            # Шаг 2: Добавляем все созданные объекты в сессию SQLAlchemy
            # Это "регистрирует" наши намерения на запись в БД, но еще не записывает.
            db.session.add_all(posts_objects)
            print("\nОбъекты добавлены в сессию SQLAlchemy.")

            # Шаг 3: Сохраняем (коммитим) все изменения из сессии в базу данных
            # На этом шаге выполняются реальные SQL INSERT команды.
            db.session.commit()
            print("Данные успешно сохранены в базе данных!")

            # (Необязательно) Выведем добавленные посты, чтобы увидеть ID, присвоенные базой
            print("\nДобавленные записи (с присвоенными ID):")
            for post in posts_objects:
                # Теперь у каждого объекта post есть атрибут 'id'
                print(f"  - {post}") # Используется метод __repr__

        except Exception as e:
            # Если во время db.session.commit() произошла ошибка
            # (например, файл БД заблокирован, или нарушено какое-то ограничение),
            # необходимо отменить все изменения, подготовленные в этой сессии.
            db.session.rollback() # Откат транзакции
            print(f"\n!!! Произошла ошибка при сохранении данных: {e}")
            print("Все изменения для этой сессии были отменены (rollback).")


# --- 6. Запуск функции добавления данных ---
# Эта стандартная конструкция Python проверяет, запущен ли файл
# как основной скрипт (а не импортирован в другой файл).
if __name__ == '__main__':
    add_some_addresses() # Вызываем функцию добавления данных
    print(f"\nСкрипт 'add_address_data.py' завершил работу.")

# --- (Конец кода в add_address_data.py) ---