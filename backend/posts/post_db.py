import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func  # Импортируем func для использования функций SQL типа COUNT

# --- 1. Настройка Flask приложения ---
# Снова создаем экземпляр Flask, так как SQLAlchemy нужен контекст приложения
# для доступа к конфигурации базы данных.
app = Flask(__name__)

# --- 2. Настройка Базы Данных ---
# Указываем ТОЧНО ТОТ ЖЕ путь к файлу базы данных 'address_posts.db',
# из которого мы хотим читать данные.
basedir = os.path.abspath(os.path.dirname(__file__))
db_filename = 'address_posts.db'
db_path = os.path.join(basedir, db_filename)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Чтение данных из базы: {db_path}")

# --- 3. Инициализация SQLAlchemy ---
# Создаем объект 'db', связанный с нашим приложением.
db = SQLAlchemy(app)


# --- 4. Определение МОДЕЛИ Posts ---
# КРАЙНЕ ВАЖНО: Даже для чтения данных, SQLAlchemy нужно знать структуру
# таблицы. Поэтому мы определяем модель Posts ЗДЕСЬ точно так же,
# как она была определена при создании БД и добавлении данных.
# Это позволяет SQLAlchemy преобразовывать строки из базы данных
# в удобные объекты Python (экземпляры класса Posts).
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    relative_address = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        # Удобное представление объекта для вывода
        return f'<Post ID: {self.id}, Address: {self.relative_address[:60]}...>'


# --- 5. Функция для выполнения запросов на чтение данных ---
def query_posts_data():
    print("\n--- Начинаем запросы к базе данных ---")

    # Используем контекст приложения Flask для выполнения операций с БД
    with app.app_context():
        try:
            # --- Запрос 1: Получить ВСЕ записи из таблицы 'posts' ---
            print("\n1. Получение всех постов (отсортировано по ID):")
            # Создаем объект запроса: выбрать всё (*) из таблицы Posts, отсортировать по id
            all_posts_query = db.select(Posts).order_by(Posts.id)
            # Выполняем запрос и получаем результаты как список объектов Posts
            # .scalars() извлекает первый элемент из каждой строки результата (наш объект Posts)
            # .all() собирает все результаты в список Python
            all_posts = db.session.execute(all_posts_query).scalars().all()

            if all_posts:
                for post in all_posts:
                    # Печатаем каждую запись, используя метод __repr__
                    print(f"  - {post}")
            else:
                print("  В таблице 'posts' нет записей.")

            # --- Запрос 2: Получить ОДНУ запись по её ID ---
            post_id_to_find = 2  # Попробуем найти пост с ID=2
            print(f"\n2. Поиск поста с ID = {post_id_to_find}:")
            # Создаем запрос: выбрать из Posts, где id равен post_id_to_find
            # filter_by используется для простых равенств "поле = значение"
            single_post_query = db.select(Posts).filter_by(id=post_id_to_find)
            # Выполняем запрос и ожидаем ОДИН или НОЛЬ результатов
            # .scalar_one_or_none() идеально подходит для этого:
            # возвращает объект, если найдена одна строка, или None, если строк 0 или больше 1.
            found_post = db.session.execute(single_post_query).scalar_one_or_none()

            if found_post:
                print(f"  Найден пост: {found_post}")
            else:
                print(f"  Пост с ID={post_id_to_find} не найден.")

            # --- Запрос 3: Получить записи, удовлетворяющие УСЛОВИЮ ---
            search_term = "/static/"
            print(f"\n3. Поиск постов, где адрес содержит '{search_term}':")
            # Создаем запрос: выбрать из Posts, где поле relative_address СОДЕРЖИТ search_term
            # Используем метод .filter() для более сложных условий
            # Posts.relative_address.contains() генерирует SQL LIKE '%search_term%'
            filter_query = db.select(Posts).filter(Posts.relative_address.contains(search_term))
            # Выполняем запрос и получаем все найденные объекты
            filtered_posts = db.session.execute(filter_query).scalars().all()

            if filtered_posts:
                print(f"  Найдены посты:")
                for post in filtered_posts:
                    print(f"    - {post}")
            else:
                print(f"  Посты, содержащие '{search_term}' в адресе, не найдены.")

            # --- Запрос 4: Подсчитать общее количество записей ---
            print("\n4. Подсчет общего количества постов:")
            # Создаем запрос: посчитать количество записей (COUNT(id)) в таблице Posts
            # Используем func.count() из SQLAlchemy
            count_query = db.select(func.count(Posts.id))
            # Выполняем запрос и ожидаем ОДНО скалярное значение (число)
            # .scalar_one() подходит для получения единственного значения из результата
            total_posts = db.session.execute(count_query).scalar_one()
            print(f"  Всего записей в таблице 'posts': {total_posts}")

        except Exception as e:
            # Обработка возможных ошибок при доступе к БД
            print(f"\n!!! Произошла ошибка во время выполнения запроса: {e}")


# --- 6. Запуск функции запроса данных ---
# Стандартная проверка, чтобы код выполнялся только при прямом запуске скрипта
if __name__ == '__main__':
    query_posts_data()  # Вызываем нашу функцию
    print(f"\n--- Скрипт 'query_address_data.py' завершил работу ---")

# --- (Конец кода в query_address_data.py) ---
