from flask import (
    Blueprint, g, render_template, request, redirect, url_for
)
from dances.db import get_db
from datetime import date

bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET','POST'])
def index():
    database = get_db()
    current_date = date.today().isoformat()
    
    search_query = request.args.get('search', '')
    
    if search_query:
        # Search in dance name, step name, and source
        dances = database.execute("""
            SELECT d.ID, d.DanceName, d.Video, d.Source
            FROM Dance d
            WHERE d.DanceName LIKE ? OR d.Source LIKE ?""",
            (f'%{search_query}%', f'%{search_query}%')
        ).fetchall()
    else:
        # Get all dances
        dances = database.execute(
            'SELECT d.ID, d.DanceName, d.Video, d.Source FROM Dance d'
        ).fetchall()
    
    # If user is logged in, get their learned and learning dances
    user_learned = []
    user_learning = []
    if g.user:
        user_id = g.user['Username']
        user_learned = database.execute(
            'SELECT DanceId FROM Learned WHERE UserId = ?',
            (user_id,)
        ).fetchall()
        user_learned = [f['DanceId'] for f in user_learned]
        
        user_learning = database.execute(
            'SELECT DanceId FROM Learning WHERE UserId = ?',
            (user_id,)
        ).fetchall()
        user_learning = [l['DanceId'] for l in user_learning]
        
    return render_template('index.html', dances=dances, 
                          user_favorites=user_learned, 
                          user_learning=user_learning,
                          current_date=current_date)
