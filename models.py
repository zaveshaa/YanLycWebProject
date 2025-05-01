from extensions import db

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    habit = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    progress = db.Column(db.Integer, default=0)
    tree_stage = db.Column(db.Integer, default=1)
    seed = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    plants = db.relationship('Plant', backref='user', lazy=True)