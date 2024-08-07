from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Question, QuizResult, QuizSet, Feedback
from app.forms import RegistrationForm, LoginForm
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
        user.role = form.role.data  # Set role
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
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

@main_bp.route("/student_dashboard")
@login_required
def student_dashboard():
    user_results = QuizResult.query.filter_by(user_id=current_user.id).all()
    total_questions = sum(len(result.quiz_set.questions) for result in user_results)
    total_score = sum(result.score for result in user_results)
    return render_template('student_dashboard.html', total_questions=total_questions, total_score=total_score, results=user_results)

@main_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    return render_template('admin_dashboard.html')

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
    quiz_sets = QuizSet.query.all()
    if request.method == 'POST':
        text = request.form['text']
        options = request.form['options']
        correct_option = request.form['correct_option']
        quiz_set_id = request.form['quiz_set_id']
        question = Question(text=text, options=options, correct_option=correct_option, quiz_set_id=quiz_set_id, user_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.admin_dashboard'))
    return render_template('add_question.html', quiz_sets=quiz_sets)

@main_bp.route('/admin/add_quiz_set', methods=['GET', 'POST'])
@login_required
def add_quiz_set():
    if request.method == 'POST':
        title = request.form['title']
        quiz_set = QuizSet(title=title)
        db.session.add(quiz_set)
        db.session.commit()
        return redirect(url_for('main.add_question'))
    return render_template('add_quiz_set.html')

@main_bp.route("/available_tests")
@login_required
def available_tests():
    quizzes = QuizSet.query.all()
    return render_template('available_tests.html', quizzes=quizzes)

@main_bp.route('/admin/view_feedback')
@login_required
def view_feedback():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    feedbacks = QuizResult.query.all()
    return render_template('view_feedback.html', feedbacks=feedbacks)

@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

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
        if current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        data = request.get_json()
        question = Question(
            text=data['text'],
            options=','.join(data['options']),
            correct_option=data['correct_option'],
            quiz_set_id=data['quiz_set_id'],
            user_id=current_user.id
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question added successfully'}), 201
