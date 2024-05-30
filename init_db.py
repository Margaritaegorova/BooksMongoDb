from pymongo import MongoClient
from werkzeug.security import generate_password_hash

client = MongoClient('mongodb://localhost:27017/')
db = client['new_project_db']

# Добавление пользователей в MongoDB с хешированием паролей
users = db['users']
users.insert_many([
    {"username": "admin", "password": generate_password_hash("admin123"), "role": "admin"},
    {"username": "editor", "password": generate_password_hash("editor123"), "role": "editor"},
    {"username": "viewer", "password": generate_password_hash("viewer123"), "role": "viewer"},
])

# Создание коллекций
books = db['books']
authors = db['authors']

# Добавление данных в коллекции
authors.insert_many([
    {"name": "J.K. Rowling"},
    {"name": "J.R.R. Tolkien"},
    {"name": "George R.R. Martin"},
])

books.insert_many([
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling", "published_year": 1997},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien", "published_year": 1937},
    {"title": "A Game of Thrones", "author": "George R.R. Martin", "published_year": 1996},
])
