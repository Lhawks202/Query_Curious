from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
        render_template_string)
from dances.db import get_db

bp = Blueprint('favorites', __name__, url_prefix='/favorites')

@bp.route('/', methods=['GET', 'POST'],)
def favorites():
    if request.method == 'POST':
        pass
    db = get_db()
    # add an error if the user is not logged in?
    if g.user is None:
        return render_template('favorites.html')
    favorite_dances = db.execute(
                            '''SELECT d.DanceName as dance_name, f.DateAdded as date_added, f.Rating as rating
                             FROM Favorites f JOIN Dance d ON f.DanceId = d.ID
                             WHERE UserId = ?''',
                            (g.user['UserID'],)).fetchall()
    
    dance_information = db.execute(
            '''SELECT d.ID, d.DanceName, d.Video, d.Source, s.StepName
             FROM Favorites f JOIN Dance d ON f.DanceId = d.ID 
             JOIN Steps s ON s.DanceId = d.ID
             WHERE UserId = ?''',
            (g.user['UserID'],)).fetchall()
    return render_template('favorites.html', favorites=favorite_dances, dances=dance_information)