from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///garden.db'
db = SQLAlchemy(app)

# Модели БД
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    session_token = db.Column(db.String(120))  # Для простой аутентификации
    plants = db.relationship('Plant', backref='user')

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    habit = db.Column(db.String(80))
    level = db.Column(db.Integer, default=0)
    progress = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Проверка авторизации через куки
def get_current_user():
    session_token = request.cookies.get('session_token')
    if session_token:
        return User.query.filter_by(session_token=session_token).first()
    return None

# Главная страница
@app.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    plants = Plant.query.filter_by(user_id=user.id).all()
    return render_template('index.html', plants=plants, username=user.username)  # Передаем username явно

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя уже занято!', 'error')
            return redirect(url_for('register'))

        user = User(username=username, password=hashed_password, session_token=str(uuid.uuid4()))
        db.session.add(user)
        db.session.commit()

        # Создаем дефолтные растения для нового пользователя
        plants = [
            Plant(name="Кактус", habit="перерыв", user_id=user.id),
            Plant(name="Дуб", habit="спорт", user_id=user.id)
        ]
        db.session.add_all(plants)
        db.session.commit()

        response = make_response(redirect(url_for('index')))
        response.set_cookie('session_token', user.session_token)
        return response
    return render_template('register.html')

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            user.session_token = str(uuid.uuid4())  # Обновляем токен
            db.session.commit()
            response = make_response(redirect(url_for('index')))
            response.set_cookie('session_token', user.session_token)
            return response
        flash('Неверный логин или пароль!', 'error')
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.set_cookie('session_token', '', expires=0)
    return response

# Обновление прогресса растения
@app.route('/update/<int:plant_id>', methods=['POST'])
def update(plant_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    plant = Plant.query.get_or_404(plant_id)
    if plant.user_id == user.id:
        plant.progress += 10
        if plant.progress >= 100:
            plant.level += 1
            plant.progress = 0
            flash(f'🎉 {plant.name} вырос до уровня {plant.level}!', 'success')
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)