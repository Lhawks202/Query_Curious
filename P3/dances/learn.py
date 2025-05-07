from flask import (
    Blueprint, g, render_template, request, jsonify)
from dances.db import get_db
from dances.auth import login_required
from collections import defaultdict

bp = Blueprint('learn', __name__)

@bp.route('/learned', methods=['GET', 'POST'],)
@login_required
def learned():
    if request.method == 'POST':
        data = request.get_json()
        action = data['action']
        if action == 'remove':
            ret_status = remove_from_learned(data)
        else:
            ret_status = add_learned(data)
        return jsonify(status=ret_status)
    db = get_db()
    if g.user is None:
        return render_template('learned.html')
    

    raw_rows = db.execute(
    '''SELECT d.ID as dance_id, d.DanceName as dance_name, 
                    learn.DateAdded as date_added, learn.Rating as rating
                    , s.StepName as step_name, fs.Place as place, 
                    fig.Name as figure_name
       FROM Learned learn
       JOIN Dance d ON learn.DanceId = d.ID 
       JOIN Steps s ON s.DanceId = d.ID
       JOIN FigureStep fs ON fs.StepsId = s.ID
       JOIN Figure fig ON fig.ID = fs.FigureId
       WHERE learn.UserId = ?
       ORDER BY d.ID, s.StepName, fs.Place
    ''',
    (g.user['Username'],)).fetchall()

    

    learned_dances = {}

    for row in raw_rows:
        d_id   = row['dance_id']
        step   = row['step_name']
        figure = row['figure_name']
        place  = row['place']

        if d_id not in learned_dances:
            learned_dances[d_id] = {
                'dance_id': row['dance_id'],
                'dance_name': row['dance_name'],
                'date_added': row['date_added'],
                'rating': row['rating'],
                'steps': defaultdict(list),
            }

        learned_dances[d_id]['steps'][step].append((place, figure))

    # Sort figures by their numeric place
    for dance in learned_dances.values():
        dance['steps'] = {
            step: [name for place, name in sorted(fig_list)]
            for step, fig_list in dance['steps'].items()
        }

    return render_template('learned.html', learned=learned_dances)

def add_learned(data):
    db = get_db()
    dance_id = data['danceId']
    rating = data['rating']
    date = data['date']
    user_id = g.user['Username']
    db.execute(
        '''INSERT INTO Learned (UserId, DanceId, DateAdded, Rating)
         VALUES (?, ?, ?, ?)''',
         (user_id, dance_id, date, rating)
    )
    db.commit()
    # TO DO: add error handling
    return "added"

def remove_from_learned(data):
    db = get_db()
    dance_id = data['danceId']
    user_id = g.user['Username']
    db.execute('DELETE FROM Learned WHERE UserId = ? AND DanceId = ?',
                   (user_id, dance_id))
    db.commit()
    return "removed"


@bp.route('/learning', methods=['GET', 'POST'])
@login_required
def learning():
    if request.method == 'POST':
        data = request.get_json()
        action = data['action']
        if action == 'remove':
            ret_status = remove_from_learning(data)
        else:
            ret_status = add_learning(data)
        return jsonify(status=ret_status)
    db = get_db()
    # add an error if the user is not logged in?
    if g.user is None:
        return render_template('learning.html')
    
    raw_rows = db.execute(
    '''SELECT d.ID as dance_id, d.DanceName as dance_name, 
                    learn.DateAdded as date_added
                    , s.StepName as step_name, fs.Place as place, 
                    fig.Name as figure_name
       FROM Learning learn
       JOIN Dance d ON learn.DanceId = d.ID 
       JOIN Steps s ON s.DanceId = d.ID
       JOIN FigureStep fs ON fs.StepsId = s.ID
       JOIN Figure fig ON fig.ID = fs.FigureId
       WHERE learn.UserId = ?
       ORDER BY d.ID, s.StepName, fs.Place
    ''',
    (g.user['Username'],)).fetchall()

    

    learning_dances = {}

    for row in raw_rows:
        d_id   = row['dance_id']
        step   = row['step_name']
        figure = row['figure_name']
        place  = row['place']

        if d_id not in learning_dances:
            learning_dances[d_id] = {
                'dance_id': row['dance_id'],
                'dance_name': row['dance_name'],
                'date_added': row['date_added'],
                'steps': defaultdict(list),
            }

        learning_dances[d_id]['steps'][step].append((place, figure))

    # Sort figures by their numeric place
    for dance in learning_dances.values():
        dance['steps'] = {
            step: [name for place, name in sorted(fig_list)]
            for step, fig_list in dance['steps'].items()
        }
    
    
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

def remove_from_learning(data):
    db = get_db()
    dance_id = data['danceId']
    user_id = g.user['Username']
    db.execute('DELETE FROM Learning WHERE UserId = ? AND DanceId = ?',
                   (user_id, dance_id))
    db.commit()
    return "removed"