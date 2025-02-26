from app import create_app, db
from flask_migrate import Migrate
from flask import request
from flask_babel import Babel
from config import Config

def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

app = create_app()

babel = Babel(app, locale_selector=get_locale)

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True)
