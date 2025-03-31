from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from . import mysql

admin = Blueprint('admin', __name__)


def admin_required():
    if 'loggedin' not in session or session.get('role') not in ['admin', 'staff']:
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))


@admin.route('/admin/dashboard')
def admin_dashboard():
    if 'loggedin' not in session or session.get('role') != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT Person.name, Person.email, Users.role
        FROM Users
        JOIN Person ON Users.person_ID = Person.person_ID
        WHERE Users.person_ID = %s
    """, (session['id'],))
    user_data = cursor.fetchone()
    cursor.close()

    return render_template('admin_dashboard.html', user=user_data)




@admin.route('/admin/users')
def manage_users():
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Users.person_ID, Person.name, Person.email, Users.role FROM Users JOIN Person ON Users.person_ID = Person.person_ID")
    users = cursor.fetchall()
    cursor.close()
    
    return render_template('admin_users.html', users=users)

@admin.route('/promote-to-staff/<int:user_id>')
def promote_to_staff(user_id):
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Users SET role = 'staff' WHERE person_ID = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()

    flash("User promoted to staff!", "success")
    return redirect(url_for('admin.manage_users'))

@admin.route('/demote-to-user/<int:user_id>')
def demote_to_user(user_id):
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Users SET role = 'user' WHERE person_ID = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()

    flash("User demoted to regular user!", "success")
    return redirect(url_for('admin.manage_users'))

@admin.route('/admin/classes')
def manage_classes():
    if 'loggedin' not in session or session.get('role') not in ['staff', 'admin']:
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    if session.get('role') == 'admin':
        cursor.execute("""
            SELECT Classes.class_ID, Classes.name, Classes.time, Classes.date,
                   Person.name AS coach_name, Locations.branch
            FROM Classes
            JOIN Staff ON Classes.person_ID = Staff.person_ID
            JOIN Person ON Staff.person_ID = Person.person_ID
            JOIN Locations ON Classes.location_ID = Locations.location_ID
        """)
    else:
        cursor.execute("""
            SELECT Classes.class_ID, Classes.name, Classes.time, Classes.date,
                   Person.name AS coach_name, Locations.branch
            FROM Classes
            JOIN Staff ON Classes.person_ID = Staff.person_ID
            JOIN Person ON Staff.person_ID = Person.person_ID
            JOIN Locations ON Classes.location_ID = Locations.location_ID
            WHERE Staff.person_ID = %s
        """, (session['id'],))

    classes = cursor.fetchall()
    cursor.close()

    return render_template('admin_classes.html', classes=classes)



