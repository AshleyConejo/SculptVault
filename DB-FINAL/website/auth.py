from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
from . import mysql 

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier')  
        password = request.form.get('password')

        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT users.person_ID, users.password, users.role, person.username 
            FROM users 
            JOIN person ON users.person_ID = person.person_ID 
            WHERE person.email = %s OR person.username = %s
        """, (login_identifier, login_identifier))
        
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[3]
            session['role'] = user[2]

            if user[2] in ['staff', 'admin']:
                return redirect(url_for('admin.admin_dashboard'))

            return redirect('/dashboard')

    return render_template('login.html')


@auth.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')  
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM person WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return render_template('register.html', error="Username already taken.")

        cursor.execute(
            "INSERT INTO person (name, username, email, phone_number) VALUES (%s, %s, %s, %s)", 
            (name, username, email, phone_number)
        )
        mysql.connection.commit()

        person_id = cursor.lastrowid
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (person_ID, password, role) VALUES (%s, %s, %s)", 
            (person_id, hashed_password, 'user')
        )
        mysql.connection.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')





