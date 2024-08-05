from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Question, QuizResult, QuizSet
from app.forms import RegistrationForm, LoginForm
from flask import Blueprint, jsonify
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


@main_bp.route("/quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    quiz = QuizSet.query.get_or_404(quiz_id)
    if request.method == 'POST':
        score = 0
        total = len(quiz.questions)
        for question in quiz.questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1
        result = QuizResult(user_id=current_user.id, score=score)
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('main.results', score=score, total=total))
    return render_template('quiz.html', quiz=quiz)

@main_bp.route("/results")
@login_required
def results():
    score = request.args.get('score', type=int)
    total = request.args.get('total', type=int)
    return render_template('results.html', score=score, total=total)


@main_bp.route('/admin/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    if request.method == 'POST':
        text = request.form['text']
        options = request.form['options']
        correct_option = request.form['correct_option']
        quiz_set_id = request.form['quiz_set_id']
        question = Question(text=text, options=options, correct_option=correct_option, quiz_set_id=quiz_set_id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_question.html')

class QuizQuestionsAPI(Resource):
    def get(self, quiz_set_id):
        questions = Question.query.filter_by(quiz_set_id=quiz_set_id).all()
        return jsonify([{
            'id': q.id,
            'text': q.text,
            'options': q.options.split(','),
            'correct_option': q.correct_option
        } for q in questions])

class AddQuestionAPI(Resource):
    @login_required
    def post(self):
        data = request.get_json()
        question = Question(
            text=data['text'],
            options=','.join(data['options']),
            correct_option=data['correct_option'],
            quiz_set_id=data['quiz_set_id']
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question added successfully'}), 201
    
@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))