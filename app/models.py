from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(64), nullable=False)
    questions = db.relationship('Question', backref='author', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)
    options = db.Column(db.String(256), nullable=False)
    correct_option = db.Column(db.String(64), nullable=False)
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    feedbacks = db.relationship('Feedback', backref='question', lazy=True)


class QuizSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    questions = db.relationship('Question', backref='quiz_set', lazy=True)
    quiz_results = db.relationship('QuizResult', backref='related_quiz_set', lazy=True)  # Renamed backref


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_set_id = db.Column(db.Integer, db.ForeignKey('quiz_set.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_set = db.relationship('QuizSet', backref='results')  # Keep this backref


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.String(256), nullable=False)
