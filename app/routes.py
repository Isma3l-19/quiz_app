from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models import User, Question, QuizResult, QuizSet, Feedback
from app.forms import RegistrationForm, LoginForm
from flask_restful import Api, Resource

# Blueprint for main routes and API routes
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Home page route
@main_bp.route("/")
def index():
    return render_template('index.html')

# Registration route
@main_bp.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user and add to the database
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# Login route
@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', form=form)

# Student dashboard route
@main_bp.route("/student_dashboard")
@login_required
def student_dashboard():
    # Get user's quiz results and calculate total score
    user_results = QuizResult.query.filter_by(user_id=current_user.id).all()
    total_questions = sum(len(result.quiz_set.questions) for result in user_results)
    total_score = sum(result.score for result in user_results)
    quiz_sets = QuizSet.query.all()  # Get all quiz sets
    return render_template(
        'student_dashboard.html', 
        total_questions=total_questions, 
        total_score=total_score, 
        results=user_results,
        quiz_sets=quiz_sets  # Pass quiz sets to template
    )

# Admin dashboard route
@main_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    # Get all students and their quiz result count
    students = User.query.filter_by(role='student').all()
    for student in students:
        student.completed_quizzes_count = QuizResult.query.filter_by(user_id=student.id).count()
    return render_template('admin_dashboard.html', students=students)

# Quiz-taking route
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
        # Save quiz result
        result = QuizResult(user_id=current_user.id, quiz_set_id=quiz.id, score=score)
        db.session.add(result)
        db.session.commit()
        return redirect(url_for('main.results', score=score, total=total))
    return render_template('quiz.html', quiz=quiz)

# Display quiz results
@main_bp.route("/results")
@login_required
def results():
    score = request.args.get('score', type=int)
    total = request.args.get('total', type=int)
    return render_template('results.html', score=score, total=total)

# Add new question (Admin only)
@main_bp.route('/admin/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    quiz_sets = QuizSet.query.all()
    if request.method == 'POST':
        # Get question details from form
        text = request.form['text']
        options = request.form['options']
        correct_option = request.form['correct_option']
        quiz_set_id = request.form['quiz_set_id']
        # Add new question to database
        question = Question(text=text, options=options, correct_option=correct_option, quiz_set_id=quiz_set_id, user_id=current_user.id)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.admin_dashboard'))
    return render_template('add_question.html', quiz_sets=quiz_sets)

# Add new quiz set (Admin only)
@main_bp.route('/admin/add_quiz_set', methods=['GET', 'POST'])
@login_required
def add_quiz_set():
    if request.method == 'POST':
        # Add new quiz set to database
        title = request.form['title']
        quiz_set = QuizSet(title=title)
        db.session.add(quiz_set)
        db.session.commit()
        return redirect(url_for('main.add_question'))
    return render_template('add_quiz_set.html')

# List available tests
@main_bp.route("/available_tests")
@login_required
def available_tests():
    quizzes = QuizSet.query.all()
    return render_template('available_tests.html', quizzes=quizzes)

# View feedback for admins
@main_bp.route('/admin/view_feedback')
@login_required
def view_feedback():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    feedbacks = QuizResult.query.all()  # Get all feedbacks
    return render_template('view_feedback.html', feedbacks=feedbacks)

# Review a specific student (Admin only)
@main_bp.route('/admin/review_student/<int:student_id>')
@login_required
def review_student(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    student = User.query.get_or_404(student_id)
    quiz_results = QuizResult.query.filter_by(user_id=student.id).all()
    return render_template('review_student.html', student=student, quiz_results=quiz_results)

# Review a specific question (Admin only)
@main_bp.route('/admin/review_question/<int:result_id>', methods=['GET', 'POST'])
@login_required
def review_question(result_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    result = QuizResult.query.get_or_404(result_id)
    if request.method == 'POST':
        # Add admin comment to the result
        comment = request.form['comment']
        result.admin_comment = comment
        db.session.commit()
        return redirect(url_for('main.review_student', student_id=result.user_id))
    return render_template('review_questions.html', result=result)

# Logout route
@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# API to get quiz questions
class QuizQuestionsAPI(Resource):
    def get(self, quiz_set_id):
        questions = Question.query.filter_by(quiz_set_id=quiz_set_id).all()
        return jsonify([{
            'id': q.id,
            'text': q.text,
            'options': q.options.split(','),
            'correct_option': q.correct_option
        } for q in questions])

# API to add a new question (Admin only)
class AddQuestionAPI(Resource):
    @login_required
    def post(self):
        if current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 403
        data = request.get_json()
        # Add question to the database
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
