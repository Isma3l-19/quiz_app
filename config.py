import os 


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'helloworld'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True #it was false