from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from dances.db import get_db
from dances.auth import login_required

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/', methods=['GET'])
@login_required
def view_profile():
    """View user profile information."""
    return render_template('profile.html', user=g.user)

@bp.route('/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information."""
    name = request.form['name']
    email = request.form['email']
    state = request.form['state']
    city = request.form['city']
    
    error = None
    
    if not name:
        error = 'Name is required.'
    elif not email:
        error = 'Email is required.'
    
    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            """UPDATE User 
               SET Name = ?, Email = ?, State = ?, City = ?, updated_at = CURRENT_TIMESTAMP
               WHERE Username = ?""",
            (name, email, state, city, g.user['Username'])
        )
        db.commit()
        flash('Profile updated successfully!')
        
    return redirect(url_for('profile.view_profile')) 