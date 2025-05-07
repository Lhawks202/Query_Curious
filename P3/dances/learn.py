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
    
    dances = db.execute(
        '''
        SELECT d.ID as id, d.DanceName as dance_name, l.DateAdded as date_added
        FROM Learning l
        JOIN Dance d ON l.DanceID = d.ID
        WHERE l.UserID = ?
        ''', (g.user['Username'],)
    ).fetchall()

    learning_dances = {}
    figures = {}

    for dance in dances:
        dance_id = dance['id']
        dance_name = dance['dance_name']
        date_added = dance['date_added']
        steps_and_figures = db.execute(
            '''
            SELECT s.StepName as step_name, 
                   f.ID as figure_id, 
                   f.Name as figure_name, 
                   f.Duration as duration, 
                   f.StartPosition as start_position, 
                   f.EndPosition as end_position, 
                   f.Action as action, 
                   fs.Place as place
            FROM Step s
            JOIN FigureStep fs ON fs.StepID = s.ID
            JOIN Figure f ON f.ID = fs.FigureID
            WHERE DanceID = ?
            ORDER BY s.StepName, fs.Place ASC
            ''', (dance_id,)
        ).fetchall()

        # if there are no steps/figures for this dance, warn and continue (shouldn't happen)
        if len(steps_and_figures) == 0: 
            print(f"Warning: no steps/figures associated with dance {dance_name} (id: {dance_id})")
            continue
        
        learning_dances[dance_name] = {}
        learning_dances[dance_name]['steps'] = {}
        
        for s in steps_and_figures:
            # if step already in return object, simply append the figure
            current_step = s['step_name']
            current_figure_id = s['figure_id']
            current_figure_name = s['figure_name']
            
            # Store figure details
            if current_figure_id not in figures:
                figures[current_figure_id] = {
                    'name': current_figure_name,
                    'duration': s['duration'],
                    'start_position': s['start_position'],
                    'end_position': s['end_position'],
                    'action': s['action']
                }
            
            # Store figure ID in steps dictionary
            if current_step in learning_dances[dance_name]['steps']:
                learning_dances[dance_name]['steps'][current_step].append(current_figure_id)
            else:
                learning_dances[dance_name]['steps'][current_step] = [current_figure_id]
            
        learning_dances[dance_name]['date_added'] = date_added
        learning_dances[dance_name]['dance_id'] = dance_id
        
    print(learning_dances)
    print(figures)
    return render_template('learning.html', learning=learning_dances, figures=figures)

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