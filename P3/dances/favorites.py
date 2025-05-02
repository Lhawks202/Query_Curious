from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
        render_template_string)
from dances.db import get_db

bp = Blueprint('favorites', __name__, url_prefix='/favorites')

@bp.route('/', methods=['GET', 'POST'],)
def favorite_dances():
    if request.method == 'POST':
        pass
    db = get_db()
    if g.user is None:
        return render_template('favorites.html')
    favorite_dances = db.execute(
                            'SELECT Dance.DanceName, Favorites.DateAdded, Favorites.Rating '
                            'FROM Favorites '
                            'JOIN Dance ON Favorites.DanceId = Dance.ID'
                            'WHERE UserId = ?', (g.user['UserID'],)).fetchall()
    return render_template('favorites.html', favorites=favorite_dances)