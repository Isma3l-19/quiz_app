from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    # Import and register blueprints
    from app.routes import main_bp, api_bp, QuizQuestionsAPI, AddQuestionAPI
    api = Api(api_bp)
    api.add_resource(QuizQuestionsAPI, '/quiz/<int:quiz_set_id>/questions', endpoint='quiz_questions')
    api.add_resource(AddQuestionAPI, '/add_question', endpoint='add_question')

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
