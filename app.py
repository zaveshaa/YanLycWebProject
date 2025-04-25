from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from tree_generator import TreeGenerator
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///garden.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)
tree_gen = TreeGenerator()

# Импорт моделей после инициализации db
with app.app_context():
    from models import User, Plant


def get_current_user():
    user_id = request.cookies.get('user_id')
    if user_id:
        return User.query.get(int(user_id))
    return None


@app.route('/')
def index():
    user = get_current_user()
    if user:
        return redirect(url_for('profile'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Это имя пользователя уже занято', 'error')
            return redirect(url_for('register'))

        user = User(
            username=username,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        # Создаем стартовые растения
        plants = [
            Plant(name='Дуб', habit='спорт', user_id=user.id),
            Plant(name='Клен', habit='чтение', user_id=user.id),
            Plant(name='Яблоня', habit='вода', user_id=user.id)
        ]
        db.session.add_all(plants)
        db.session.commit()

        response = redirect(url_for('profile'))
        response.set_cookie('user_id', str(user.id))
        return response

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            response = redirect(url_for('profile'))
            response.set_cookie('user_id', str(user.id))
            return response

        flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    response = redirect(url_for('index'))
    response.set_cookie('user_id', '', expires=0)
    return response


# ... (остальной код остается тем же)

@app.route('/profile')
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    plants = Plant.query.filter_by(user_id=user.id).all()
    plant_trees = {}

    for plant in plants:
        # Генерируем дерево и заменяем ANSI-цвета на HTML-теги
        tree_ansi = tree_gen.generate_tree(plant.tree_stage)
        tree_html = (tree_ansi
                     .replace('\033[38;2;139;69;19m', '<span class="tree-trunk">')
                     .replace('\033[38;2;160;82;45m', '<span class="tree-branch">')
                     .replace('\033[38;2;34;139;34m', '<span class="tree-leaves">')
                     .replace('\033[0m', '</span>')
                     .replace('\n', '<br>'))
        plant_trees[plant.id] = tree_html

    return render_template(
        'profile.html',
        user=user,
        plants=plants,
        plant_trees=plant_trees
    )


@app.route('/update/<int:plant_id>', methods=['POST'])
def update_plant(plant_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    plant = Plant.query.filter_by(id=plant_id, user_id=user.id).first()
    if plant:
        plant.progress += 10

        if plant.progress >= 100:
            plant.level += 1
            plant.progress = 0
            plant.tree_stage = min(plant.tree_stage + 1, 100)  # Макс 10 стадий
            flash(f'Ваше растение {plant.name} выросло до уровня {plant.level}!', 'success')

        db.session.commit()

    return redirect(url_for('profile'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
