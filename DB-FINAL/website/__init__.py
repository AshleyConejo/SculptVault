from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import os

mysql = MySQL()

def application():
    app = Flask(__name__)

    # Railway DB config
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
    app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT'))
    app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

    # Initialize MySQL
    mysql.init_app(app)

    # Register Blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    return app
