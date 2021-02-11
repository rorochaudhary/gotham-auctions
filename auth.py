import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
# need db access to authenticate
import database.db_connector as db
from datetime import date       

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['user']
        password = request.form['pass']
        db_conn = db.connect_to_database()
        error = None

        if not username:
            error = 'Username is required.'
            print(error)
        elif not password:
            error = 'Password is required.'
            print(error)
        elif db.execute_query(
            db_conn, 
            'SELECT userID FROM Users WHERE username = %s', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
            print(error)

        if error is None:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            dateJoined = date.today().strftime("%Y-%m-%d")
            db.execute_query(
                db_conn, 
                'INSERT INTO Users (userName, password, firstName, lastName, email, dateJoined) VALUES (%s, %s)',
                (username, password, fname, lname, email, dateJoined)
                # not storing hashed password for simplicity 
                # if prefer hash, use generate_password_hash(password)
            )
            
            # db.commit()
            return redirect(url_for('auth/login.j2'))

        flash(error)
    
    return render_template('auth/register.j2')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # print(f"got username: {username} and password: {password}")
        db_conn = db.connect_to_database()
        error = None

        user = db.execute_query(
            db_conn,
            'SELECT * FROM Users WHERE userName = %s', 
            (username,)
            ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif user['password'] != password:
            error = 'Incorrect password.'
        # elif not check_password_hash(user['password'], password):
        #     error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['userID']
            return redirect(url_for('root'))

        flash(error)

    return render_template('auth/login.j2')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db_conn = db.connect_to_database()
        g.user = db.execute_query(db_conn, 
            'SELECT * FROM Users WHERE userID = %s', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('root'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth/login.j2'))

        return view(**kwargs)

    return wrapped_view