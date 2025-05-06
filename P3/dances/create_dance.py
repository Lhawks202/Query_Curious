from flask import (Blueprint, render_template, session, redirect, url_for, flash, request, jsonify)
from .db import get_db
import secrets

bp = Blueprint('create', __name__, url_prefix='/create')

@bp.route('/', methods=['GET', 'POST'])
def add_dance():
    db = get_db()
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        name          = data.get('name')
        roles         = data.get('roles')
        start_pos     = data.get('start_position')
        action        = data.get('action')
        end_pos       = data.get('end_position')
        duration      = data.get('duration')

        cursor = db.execute(
            """
            INSERT INTO Figure
            (Name, Roles, StartPosition, Action, EndPosition, Duration)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, roles, start_pos, action, end_pos, duration)
        )
        new_id = cursor.lastrowid

        # **Now update the FTS table by hand**
        db.execute(
          """
          INSERT INTO FigureFTS(rowid, Name, Roles, StartPosition, Action, EndPosition)
          VALUES (?, ?, ?, ?, ?, ?)
          """,
          (new_id, name, roles, start_pos, action, end_pos)
        )
        db.commit()

        return jsonify({
            'id': new_id,
            'name': name
        }), 201

    return render_template('create/create_dance.html')

@bp.route('/search', methods=['POST'])
def search_figures():
    query = request.get_json().get('q', '').strip()
    if not query:
        return jsonify([]), 200
    
    db = get_db()
    sql = """
    SELECT F.ID, F.Name, F.Roles, F.StartPosition, F.Action, F.EndPosition, F.Duration,
        bm25(FigureFTS) AS score
    FROM FigureFTS
    JOIN Figure AS F on F.ID = FigureFTS.rowid
    WHERE FigureFTS MATCH ?
    ORDER BY score
    LIMIT 20;
    """
    param = ''.join(token + '*' for token in query.split())
    rows = db.execute(sql, (param,)).fetchall()
    results = [
      { 'id':   r['ID'],
        'name': r['Name'],
        'roles': r['Roles'],
        'start_position': r['StartPosition'],
        'action': r['Action'],
        'end_position': r['EndPosition'],
        'duration': r['Duration']
      } for r in rows
    ]
    return jsonify(results), 200