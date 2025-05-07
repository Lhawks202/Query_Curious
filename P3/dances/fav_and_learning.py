from flask import (
    Blueprint, g, render_template, request, jsonify)
from dances.db import get_db
from dances.auth import login_required

bp = Blueprint('fav_and_learning', __name__)

@bp.route('/favorites', methods=['GET', 'POST'],)
@login_required
def favorites():
    if request.method == 'POST':
        ret_status = add_favorite(request.get_json())
        return jsonify(status=ret_status)
    db = get_db()
    # add an error if the user is not logged in?
    if g.user is None:
        return render_template('favorites.html')
    
    # favorite_dances = db.execute(
    # '''
    # SELECT d.ID, d.DanceName AS dance_name, d.Video, d.Source, 
    #        f.DateAdded AS date_added, f.Rating AS rating, 
    #        s.StepName
    # FROM Favorites f
    # JOIN Dance d ON f.DanceId = d.ID
    # JOIN Steps s ON s.DanceId = d.ID
    # WHERE f.UserId = ?
    # ''',
    # (g.user['Username'],)).fetchall()
    favorite_dances = db.execute(
                            '''SELECT d.DanceName as dance_name, f.DateAdded as date_added, f.Rating as rating
                             FROM Favorites f JOIN Dance d ON f.DanceId = d.ID
                             WHERE UserId = ?''',
                            (g.user['Username'],)).fetchall()
    
    dance_information = db.execute(
            '''SELECT d.ID, d.DanceName, d.Video, d.Source, s.StepName
             FROM Favorites f JOIN Dance d ON f.DanceId = d.ID 
             JOIN Steps s ON s.DanceId = d.ID
             WHERE UserId = ?''',
            (g.user['Username'],)).fetchall()
    return render_template('favorites.html', favorites=favorite_dances)

def add_favorite(data):
    db = get_db()
    dance_id = data['danceId']
    rating = data['rating']
    date = data['date']
    user_id = g.user['Username']
    db.execute(
        '''INSERT INTO Favorites (UserId, DanceId, DateAdded, Rating)
         VALUES (?, ?, ?, ?)''',
         (user_id, dance_id, date, rating)
    )
    db.commit()
    # TO DO: add error handling
    return "added"

@bp.route('/learning', methods=['GET', 'POST'])
@login_required
def learning():
    if request.method == 'POST':
        ret_status = add_learning(request.get_json())
        return jsonify(status=ret_status)
    db = get_db()
    # add an error if the user is not logged in?
    if g.user is None:
        return render_template('learning.html')
    
    learning_dances = db.execute(
                            '''SELECT d.DanceName as dance_name, l.DateAdded as date_added
                             FROM Learning l JOIN Dance d ON l.DanceId = d.ID
                             WHERE UserId = ?''',
                            (g.user['Username'],)).fetchall()
    
    dance_information = db.execute(
            '''SELECT d.ID, d.DanceName, d.Video, d.Source, s.StepName
             FROM Learning l JOIN Dance d ON l.DanceId = d.ID 
             JOIN Steps s ON s.DanceId = d.ID
             WHERE UserId = ?''',
            (g.user['Username'],)).fetchall()
    # learning_dances = db.execute(
    # '''
    # SELECT d.ID, d.DanceName AS dance_name, d.Video, d.Source, 
    #        l.DateAdded AS date_added, s.StepName
    # FROM Learning l
    # JOIN Dance d ON l.DanceId = d.ID
    # JOIN Steps s ON s.DanceId = d.ID
    # WHERE l.UserId = ?
    # ''',
    # (g.user['Username'],)).fetchall()
    return render_template('learning.html', learning=learning_dances)

def add_learning(data):
    db = get_db()
    dance_id = data['danceId']
    date = data['date']
    user_id = g.user['Username']
    db.execute(
        '''INSERT INTO Learning (UserId, DanceId, DateAdded)
         VALUES (?, ?, ?)''',
         (user_id, dance_id, date)
    )
    db.commit()
    # TO DO: add error handling
    return "added"