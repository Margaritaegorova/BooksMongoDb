from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
bcrypt = Bcrypt(app)

# Настройка MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['new_project_db']
users_collection = db['users']
books_collection = db['books']
authors_collection = db['authors']

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, password, role):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    if not ObjectId.is_valid(user_id):
        return None
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    return User(str(user_data['_id']), user_data['username'], user_data['password'], user_data['role']) if user_data else None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        existing_user = users_collection.find_one({'username': username})
        if existing_user is None:
            hashed_password = generate_password_hash(password)
            users_collection.insert_one({'username': username, 'password': hashed_password, 'role': role})
            flash('User registered successfully!')
            return redirect(url_for('login'))
        flash('User already exists.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = users_collection.find_one({'username': username})
        if user_data and check_password_hash(user_data['password'], password):
            user = User(str(user_data['_id']), user_data['username'], user_data['password'], user_data['role'])
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

# Примеры CRUD операций для Books и Authors
@app.route('/books')
@login_required
def list_books():
    books = list(books_collection.find())
    return render_template('books.html', books=books)

@app.route('/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_books'))
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'published_year': int(request.form['published_year'])
        }
        books_collection.insert_one(data)
        return redirect(url_for('list_books'))
    authors = list(authors_collection.find())
    return render_template('add_book.html', authors=authors)

@app.route('/books/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_books'))
    if not ObjectId.is_valid(book_id):
        flash('Invalid book ID')
        return redirect(url_for('list_books'))
    book = books_collection.find_one({'_id': ObjectId(book_id)})
    if request.method == 'POST':
        data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'published_year': int(request.form['published_year'])
        }
        books_collection.update_one({'_id': ObjectId(book_id)}, {'$set': data})
        return redirect(url_for('list_books'))
    authors = list(authors_collection.find())
    return render_template('edit_book.html', book=book, authors=authors)

@app.route('/books/delete/<book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_books'))
    if not ObjectId.is_valid(book_id):
        flash('Invalid book ID')
        return redirect(url_for('list_books'))
    books_collection.delete_one({'_id': ObjectId(book_id)})
    return redirect(url_for('list_books'))

@app.route('/authors')
@login_required
def list_authors():
    authors = list(authors_collection.find())
    return render_template('authors.html', authors=authors)

@app.route('/authors/add', methods=['GET', 'POST'])
@login_required
def add_author():
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_authors'))
    if request.method == 'POST':
        data = {
            'name': request.form['name']
        }
        authors_collection.insert_one(data)
        return redirect(url_for('list_authors'))
    return render_template('add_author.html')

@app.route('/authors/edit/<author_id>', methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_authors'))
    if not ObjectId.is_valid(author_id):
        flash('Invalid author ID')
        return redirect(url_for('list_authors'))
    author = authors_collection.find_one({'_id': ObjectId(author_id)})
    if request.method == 'POST':
        data = {
            'name': request.form['name']
        }
        authors_collection.update_one({'_id': ObjectId(author_id)}, {'$set': data})
        return redirect(url_for('list_authors'))
    return render_template('edit_author.html', author=author)

@app.route('/authors/delete/<author_id>', methods=['POST'])
@login_required
def delete_author(author_id):
    if current_user.role not in ['admin', 'editor']:
        flash('Access denied')
        return redirect(url_for('list_authors'))
    if not ObjectId.is_valid(author_id):
        flash('Invalid author ID')
        return redirect(url_for('list_authors'))
    authors_collection.delete_one({'_id': ObjectId(author_id)})
    return redirect(url_for('list_authors'))

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
