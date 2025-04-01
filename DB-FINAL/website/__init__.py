from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import os

mysql = MySQL()

def application():
    app = Flask(__name__)

    # Railway DB config
    app.config['SECRET_KEY'] = 'ACHLI'
    app.config['MYSQL_HOST'] = 'shinkansen.proxy.rlwy.net'
    app.config['MYSQL_PORT'] = 48324
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'VbckqelZgKDVuQqCinBlusRoKnuvULcV'
    app.config['MYSQL_DB'] = 'railway'

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
