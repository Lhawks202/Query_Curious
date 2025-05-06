from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
        render_template_string)
from dances.db import get_db

bp = Blueprint('learning', __name__, url_prefix='/learning')

@bp.route('/', methods=['GET', 'POST'])
def learning():
    if request.method == 'POST':
        pass
    db = get_db()
    # add an error if the user is not logged in?
    if g.user is None:
        return render_template('learning.html')
    learning_dances = db.execute(
                            '''SELECT d.DanceName as dance_name, l.DateAdded as date_added
                             FROM Learning l JOIN Dance d ON l.DanceId = d.ID
                             WHERE UserId = ?''',
                            (g.user['UserID'],)).fetchall()
    
    dance_information = db.execute(
            '''SELECT d.ID, d.DanceName, d.Video, d.Source, s.StepName
             FROM Learning l JOIN Dance d ON l.DanceId = d.ID 
             JOIN Steps s ON s.DanceId = d.ID
             WHERE UserId = ?''',
            (g.user['UserID'],)).fetchall()
    return render_template('learning.html', favorites=learning_dances, dances=dance_information)