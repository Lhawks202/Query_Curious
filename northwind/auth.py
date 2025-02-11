import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from northwind.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# fetches customer from Customers by CustomerID
def fetch_customer(customer_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM Customers WHERE CustomerID = ?', (customer_id,)
    ).fetchone()

# fetches user from Authentication by UserID
def fetch_user(user_id):
    db = get_db()
    return db.execute(
        'SELECT * FROM Authentication WHERE UserID = ?', (user_id,)
    ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user_id = request.form['user_id'].lower()
        password = request.form['password']
        db = get_db()
        error = None

        if not user_id:
            error = 'User ID is required.'
        elif not password:
            error = 'Password is required.'
        
        # check if user is in Customers table
        customer = fetch_customer(user_id)
        if customer:
            error = 'Customer already exists—try logging in!'
        
        # no error, proceed
        if error is None:
            try:
                # first, create entry in the customers table
                db.execute(
                    "INSERT INTO Customers (CustomerID) VALUES (?)", (user_id,),
                )
                # then, create entry in authentication table 
                # TODO: replace session id with the session id set when the user is not authenticated
                db.execute(
                    "INSERT INTO Authentication (UserID, Password, SessionID) VALUES (?, ?, ?)",
                    (user_id, generate_password_hash(password), user_id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {user_id} is already registered."
            else:
                # TODO: redirect to correct page
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user_id = request.form['user_id'].lower() # treat user_id as case insensitive
        password = request.form['password']
        error = None

        user = fetch_user(user_id)

        if user is None:
            error = 'Incorrect user id.'
        elif not check_password_hash(user['Password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['UserID']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = fetch_user(user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view