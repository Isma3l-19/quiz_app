from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Question
from app.forms import RegistrationForm, LoginForm
from flask import Blueprint
from flask_restful import Api, Resource


main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

@main_bp.route("/")
def index():
    return render_template('index.html')

@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))


class QuizQuestionResource(Resource):
    def get(self, quiz_set_id):
        questions = Question.query.filter_by(quiz_set_id=quiz_set_id).all()
        return [{'id': q.id, 'text': q.text, 'options': q.options.split(',')} for q in questions]

api.add_resource(QuizQuestionResource, '/quiz/<int:quiz_set_id>/questions')
