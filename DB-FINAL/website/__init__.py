from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt


mysql = MySQL()

def application():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ACHLI'
    app.config['MYSQL_HOST'] = 'localhost'  
    app.config['MYSQL_USER'] = 'root'  
    app.config['MYSQL_PASSWORD'] = 'admin'  
    app.config['MYSQL_DB'] = 'gym_management'  

    from .views import views
    from .auth import auth
    from .admin import admin 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    mysql.init_app(app)

    return app
