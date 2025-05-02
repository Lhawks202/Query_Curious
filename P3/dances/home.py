from flask import (
    Blueprint, g, render_template, request
)
from dances.db import get_db

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    database = get_db()
    
    search_query = request.args.get('search', '')
    
    if search_query:
        # Search in dance name, step name, and source
        dances = database.execute(
            'SELECT d.ID, d.DanceName, d.Video, d.Date, d.Source, '
            's.StepName, s.Sequence '
            'FROM Dance d JOIN Steps s ON d.StepsId = s.ID '
            'WHERE d.DanceName LIKE ? OR s.StepName LIKE ? OR d.Source LIKE ?',
            (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        # Get all dances
        dances = database.execute(
            'SELECT d.ID, d.DanceName, d.Video, d.Date, d.Source, '
            's.StepName, s.Sequence '
            'FROM Dance d JOIN Steps s ON d.StepsId = s.ID'
        ).fetchall()
    
    # If user is logged in, get their favorites and learning dances
    user_favorites = []
    user_learning = []
    if g.user:
        user_id = g.user['UserID']
        user_favorites = database.execute(
            'SELECT DanceId FROM Favorites WHERE UserId = ?',
            (user_id,)
        ).fetchall()
        user_favorites = [f['DanceId'] for f in user_favorites]
        
        user_learning = database.execute(
            'SELECT DanceId FROM Learning WHERE UserId = ?',
            (user_id,)
        ).fetchall()
        user_learning = [l['DanceId'] for l in user_learning]
        
    return render_template('index.html', dances=dances, 
                          user_favorites=user_favorites, 
                          user_learning=user_learning)
