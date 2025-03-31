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
            SELECT Users.person_ID, Users.password, Users.role, Person.username 
            FROM Users 
            JOIN Person ON Users.person_ID = Person.person_ID 
            WHERE Person.email = %s OR Person.username = %s
        """, (login_identifier, login_identifier))
        
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            print(" User found and password matches.")
            print("Redirecting user to:", user[2])

            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[3]
            session['role'] = user[2]  

            print(f" Login successful for: {user[3]} (Role: {user[2]})")

           
            if user[2] == 'staff' or user[2] == 'admin':
                return redirect(url_for('admin.admin_dashboard'))

            return redirect('/dashboard')


        print("Invalid login attempt!")
    
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

        if not phone_number:
            print("⚠ ERROR: 'phone_number' field is missing from the form!")

        cursor = mysql.connection.cursor()

        
        cursor.execute("SELECT * FROM Person WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            print(" Username already exists!")
            return render_template('register.html', error="Username already taken.")

        
        cursor.execute(
            "INSERT INTO Person (name, username, email, phone_number) VALUES (%s, %s, %s, %s)", 
            (name, username, email, phone_number)
        )
        mysql.connection.commit()

        person_id = cursor.lastrowid
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        
        cursor.execute(
            "INSERT INTO Users (person_ID, password, role) VALUES (%s, %s, %s)", 
            (person_id, hashed_password, 'user')
        )
        mysql.connection.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')





