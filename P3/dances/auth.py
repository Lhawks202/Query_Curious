import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from dances.db import get_db
from typing import Optional, Any

bp = Blueprint('auth', __name__, url_prefix='/auth')

# fetches user from Authentication by UserID
def fetch_user(user_id: str) -> Optional[Any]:
    db = get_db()
    return db.execute(
        'SELECT * FROM Authentication WHERE UserID = ?', (user_id,)
    ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register() -> str:
    if request.method == 'POST':
        user_id = request.form['user_id'].lower()
        password = request.form['password']
        db = get_db()
        error = None

        if not user_id:
            error = 'User ID is required.'
        elif not password:
            error = 'Password is required.'
        
        # check if user is in user table
        customer = fetch_user(user_id)
        if customer:
            error = 'User already exists—try logging in!'
        
        # no error, proceed
        if error is None:
            try:
                db.execute(
                    "INSERT INTO Authentication (UserID, Password, SessionID) VALUES (?, ?, ?)",
                    (user_id, generate_password_hash(password), user_id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {user_id} is already registered."
            else:
                # TODO: redirect to correct page
                next_page = request.form.get('next') or url_for("index")
                return redirect(next_page)

        flash(error)

    next = request.args.get('next')
    return render_template('auth/register.html', next=next)

@bp.route('/login', methods=('GET', 'POST'))
def login() -> str:
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
            session['user_id'] = user['UserID']
            next = request.form['next']
            return redirect(url_for('cart.assign_user'))

        flash(error)

    next = request.args.get('next')
    return render_template('auth/login.html', next=next)

@bp.before_app_request
def load_logged_in_user() -> None:
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = fetch_user(user_id)

@bp.route('/logout')
def logout() -> str:
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view