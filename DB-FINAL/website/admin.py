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
        SELECT person.name, person.email, users.role
        FROM users
        JOIN person ON users.person_ID = person.person_ID
        WHERE users.person_ID = %s
    """, (session['id'],))
    user_data = cursor.fetchone()
    cursor.close()

    return render_template('admin_dashboard.html', user=user_data)

@admin.route('/admin/users')
def manage_users():
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT users.person_ID, person.name, person.email, users.role
        FROM users
        JOIN person ON users.person_ID = person.person_ID
    """)
    users = cursor.fetchall()
    cursor.close()

    return render_template('admin_users.html', users=users)

@admin.route('/promote-to-staff/<int:user_id>')
def promote_to_staff(user_id):
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET role = 'staff' WHERE person_ID = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()

    flash("User promoted to staff!", "success")
    return redirect(url_for('admin.manage_users'))

@admin.route('/demote-to-user/<int:user_id>')
def demote_to_user(user_id):
    if admin_required():
        return admin_required()

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET role = 'user' WHERE person_ID = %s", (user_id,))
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
            SELECT classes.class_ID, classes.name, classes.time, classes.date,
                   person.name AS coach_name, locations.branch
            FROM classes
            JOIN staff ON classes.person_ID = staff.person_ID
            JOIN person ON staff.person_ID = person.person_ID
            JOIN locations ON classes.location_ID = locations.location_ID
        """)
    else:
        cursor.execute("""
            SELECT classes.class_ID, classes.name, classes.time, classes.date,
                   person.name AS coach_name, locations.branch
            FROM classes
            JOIN staff ON classes.person_ID = staff.person_ID
            JOIN person ON staff.person_ID = person.person_ID
            JOIN locations ON classes.location_ID = locations.location_ID
            WHERE staff.person_ID = %s
        """, (session['id'],))

    classes = cursor.fetchall()
    cursor.close()

    return render_template('admin_classes.html', classes=classes)

@admin.route('/admin/classes/add', methods=['GET', 'POST'])
def add_class():
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        time = request.form['time']
        date = request.form['date']
        location_id = request.form['location_id']
        person_id = request.form['person_id']

        cursor.execute("""
            INSERT INTO classes (name, time, date, location_ID, person_ID)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, time, date, location_id, person_id))
        mysql.connection.commit()
        cursor.close()
        flash("Class added!", "success")
        return redirect(url_for('admin.manage_classes'))

    cursor.execute("SELECT location_ID, branch FROM locations")
    locations = cursor.fetchall()
    cursor.execute("""
        SELECT person.person_ID, person.name FROM person
        JOIN staff ON person.person_ID = staff.person_ID
    """)
    coaches = cursor.fetchall()
    cursor.close()

    return render_template('add_class.html', locations=locations, coaches=coaches)

@admin.route('/admin/classes/edit/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        time = request.form['time']
        date = request.form['date']
        location_id = request.form['location_id']
        person_id = request.form['person_id']

        cursor.execute("""
            UPDATE classes
            SET name = %s, time = %s, date = %s, location_ID = %s, person_ID = %s
            WHERE class_ID = %s
        """, (name, time, date, location_id, person_id, class_id))
        mysql.connection.commit()
        cursor.close()
        flash("Class updated!", "success")
        return redirect(url_for('admin.manage_classes'))

    cursor.execute("SELECT * FROM classes WHERE class_ID = %s", (class_id,))
    class_data = cursor.fetchone()

    if not class_data:
        flash("Class not found!", "error")
        return redirect(url_for('admin.manage_classes'))

    cursor.execute("SELECT location_ID, branch FROM locations")
    locations = cursor.fetchall()
    cursor.execute("""
        SELECT person.person_ID, person.name FROM person
        JOIN staff ON person.person_ID = staff.person_ID
    """)
    coaches = cursor.fetchall()
    cursor.close()

    return render_template('edit_class.html', class_data=class_data, locations=locations, coaches=coaches)



@admin.route('/admin/classes/delete/<int:class_id>')
def delete_class(class_id):
    if session.get('role') != 'admin':
        flash("Unauthorized access!", "error")
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM classes WHERE class_ID = %s", (class_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Class deleted!", "success")
    return redirect(url_for('admin.manage_classes'))
