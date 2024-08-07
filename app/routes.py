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
    quiz_sets = QuizSet.query.all()
    total_questions = QuizResult.query.filter_by(user_id=current_user.id).count()
    overall_score = db.session.query(db.func.sum(QuizResult.score)).filter_by(user_id=current_user.id).scalar() or 0
    return render_template('student_dashboard.html', quiz_sets=quiz_sets, total_questions=total_questions, overall_score=overall_score)

@main_bp.route("/take_test/<int:quiz_set_id>", methods=['GET', 'POST'])
@login_required
def take_test(quiz_set_id):
    quiz_set = QuizSet.query.get_or_404(quiz_set_id)
    question = quiz_set.questions.filter_by(completed=False).first()
    if not question:
        return redirect(url_for('main.student_dashboard'))

    if request.method == 'POST':
        selected_option = request.form.get(f'question_{question.id}')
        question.completed = True
        question.correct = (selected_option == question.correct_option)
        db.session.commit()
        next_question = quiz_set.questions.filter_by(completed=False).first()
        if next_question:
            return redirect(url_for('main.take_test', quiz_set_id=quiz_set.id))
        else:
            return redirect(url_for('main.quiz_summary', quiz_set_id=quiz_set.id))
    
    return render_template('take_test.html', quiz_set=quiz_set, question=question)

@main_bp.route("/quiz_summary/<int:quiz_set_id>")
@login_required
def quiz_summary(quiz_set_id):
    quiz_set = QuizSet.query.get_or_404(quiz_set_id)
    questions = quiz_set.questions.all()
    correct_answers = sum(1 for q in questions if q.correct)
    total_questions = len(questions)
    return render_template('quiz_summary.html', quiz_set=quiz_set, correct_answers=correct_answers, total_questions=total_questions)

@main_bp.route("/results")
@login_required
def results():
    score = request.args.get('score', type=int)
    total = request.args.get('total', type=int)
    return render_template('results.html', score=score, total=total)

@main_bp.route("/admin_dashboard")
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    return render_template('admin_dashboard.html')

@main_bp.route('/admin/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    quiz_sets = QuizSet.query.all()
    if request.method == 'POST':
        text = request.form['text']
        options = request.form['options']
        correct_option = request.form['correct_option']
        quiz_set_id = request.form['quiz_set_id']
        question = Question(text=text, options=options, correct_option=correct_option, quiz_set_id=quiz_set_id)
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

@main_bp.route('/feedback')
@login_required
def feedback():
    results = QuizResult.query.filter_by(user_id=current_user.id).all()
    feedbacks = Feedback.query.filter_by(user_id=current_user.id).all()
    return render_template('feedback.html', results=results, feedbacks=feedbacks)

@main_bp.route('/admin/review_questions', methods=['GET', 'POST'])
@login_required
def review_questions():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    
    quiz_sets = QuizSet.query.all()
    if request.method == 'POST':
        question_id = request.form['question_id']
        comment = request.form['comment']
        feedback = Feedback(user_id=request.form['user_id'], question_id=question_id, comment=comment)
        db.session.add(feedback)
        db.session.commit()
        return redirect(url_for('main.review_questions'))
    questions = Question.query.all()
    return render_template('review_questions.html', questions=questions, quiz_sets=quiz_sets)

@main_bp.route('/admin/view_feedback')
@login_required
def view_feedback():
    if current_user.role != 'admin':
        return redirect(url_for('main.login'))
    feedbacks = Feedback.query.all()
    return render_template('view_feedback.html', feedbacks=feedbacks)

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
            quiz_set_id=data['quiz_set_id']
        )
        db.session.add(question)
        db.session.commit()
        return jsonify({'message': 'Question added successfully'}), 201

@main_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# Register the API endpoints
api.add_resource(QuizQuestionsAPI, '/api/quiz_questions/<int:quiz_set_id>')
api.add_resource(AddQuestionAPI, '/api/add_question')
