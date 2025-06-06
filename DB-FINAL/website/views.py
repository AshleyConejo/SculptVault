from flask import Blueprint, render_template, request, redirect, url_for, session
from . import mysql
from MySQLdb.cursors import DictCursor

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')



@views.route('/locations')
def locations():
    cursor = mysql.connection.cursor(DictCursor)  
    cursor.execute("SELECT * FROM locations")
    locations = cursor.fetchall()
    cursor.close()

    grouped = {}
    for loc in locations:
        city = loc['city']
        if city not in grouped:
            grouped[city] = []
        grouped[city].append(loc)

    return render_template('locations.html', locations_by_city=grouped)


@views.route('/classes')
def classes():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("""
        SELECT 
            classes.name AS class_name,
            classes.time,
            classes.date,
            locations.branch AS location,
            person.name AS instructor
        FROM classes
        JOIN locations ON classes.location_ID = locations.location_ID
        JOIN person ON classes.person_ID = person.person_ID
        JOIN users ON users.person_ID = person.person_ID
        WHERE users.role = 'staff'
        ORDER BY locations.branch, classes.time
    """)
    results = cursor.fetchall()
    cursor.close()

    grouped_classes = {}
    for c in results:
        loc = c['location']
        if loc not in grouped_classes:
            grouped_classes[loc] = []
        grouped_classes[loc].append(c)

    return render_template('classes.html', grouped_classes=grouped_classes)




@views.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    # User data
    cursor.execute("""
        SELECT person.name, person.email, memberships.type 
        FROM users
        JOIN person ON users.person_ID = person.person_ID
        LEFT JOIN memberships ON users.membership_ID = memberships.membership_ID
        WHERE users.person_ID = %s
    """, (session['id'],))
    user_data = cursor.fetchone()

    # Classes the user booked
    cursor.execute("""
        SELECT user_classes.id, classes.name, classes.time, classes.date, locations.branch
        FROM user_classes
        JOIN classes ON user_classes.class_ID = classes.class_ID
        JOIN locations ON classes.location_ID = locations.location_ID
        WHERE user_classes.user_id = %s
    """, (session['id'],))
    classes = cursor.fetchall()

    # Official class options to book
    cursor.execute("""
        SELECT class_ID, name, time, date FROM classes
    """)
    available_classes = cursor.fetchall()

    cursor.close()

    return render_template(
        'dashboard.html',
        user=user_data,
        classes=classes,
        available_classes=available_classes
    )



@views.route('/membership')
def membership():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT membership_ID, type, price FROM memberships")
    memberships = cursor.fetchall()
    cursor.close()

    return render_template('membership.html', memberships=memberships)


@views.route('/select-membership', methods=['POST'])
def select_membership():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    membership_id = request.form.get('membership_id')

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET membership_ID = %s WHERE person_ID = %s", (membership_id, session['id']))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('views.dashboard'))



@views.route('/book-class', methods=['GET', 'POST'])
def book_class():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        class_id = request.form.get('class_id')

        # Check for duplicate booking
        cursor.execute("""
            SELECT * FROM user_classes
            WHERE user_id = %s AND class_ID = %s
        """, (session['id'], class_id))
        already_booked = cursor.fetchone()

        if not already_booked:
            # Get class details
            cursor.execute("""
                SELECT name, time, date, location_ID FROM classes
                WHERE class_ID = %s
            """, (class_id,))
            class_data = cursor.fetchone()

            # Get location name
            cursor.execute("""
                SELECT branch FROM locations
                WHERE location_ID = %s
            """, (class_data[3],))
            location = cursor.fetchone()[0]

            # Insert full details into user_classes
            cursor.execute("""
                INSERT INTO user_classes (user_id, class_ID, class_name, class_time, class_date, location)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['id'],
                class_id,
                class_data[0],  # name
                class_data[1],  # time
                class_data[2],  # date
                location
            ))
            mysql.connection.commit()

        cursor.close()
        return redirect(url_for('views.dashboard'))

    # Show class options in dropdown
    cursor.execute("""
        SELECT class_ID, name, time, date
        FROM classes
    """)
    classes = cursor.fetchall()
    cursor.close()

    return render_template('book_class.html', classes=classes)


@views.route('/cancel-class/<int:booking_id>')
def cancel_class(booking_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM user_classes WHERE id = %s AND user_id = %s", (booking_id, session['id']))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('views.dashboard'))


@views.route('/add-class', methods=['POST'])
def add_class():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    class_name = request.form.get('class_name')
    class_time = request.form.get('class_time')
    class_date = request.form.get('class_date')
    location = request.form.get('location')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO user_classes (user_id, class_name, class_time, class_date, location)
        VALUES (%s, %s, %s, %s, %s)
    """, (session['id'], class_name, class_time, class_date, location))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('views.dashboard'))


@views.route('/edit-class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        class_name = request.form.get('class_name')
        class_time = request.form.get('class_time')
        class_date = request.form.get('class_date')
        location = request.form.get('location')

        cursor.execute("""
            UPDATE user_classes
            SET class_name = %s, class_time = %s, class_date = %s, location = %s
            WHERE id = %s AND user_id = %s
        """, (class_name, class_time, class_date, location, class_id, session['id']))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('views.dashboard'))

    cursor.execute("SELECT * FROM user_classes WHERE id = %s AND user_id = %s", (class_id, session['id']))
    class_data = cursor.fetchone()
    cursor.close()

    return render_template('edit_class.html', class_data=class_data)


@views.route('/delete-class/<int:class_id>')
def delete_class(class_id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM user_classes WHERE id = %s AND user_id = %s", (class_id, session['id']))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('views.dashboard'))

