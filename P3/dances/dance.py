from flask import (Blueprint, render_template, redirect, url_for, request, jsonify)
from .db import get_db
import secrets, re, sqlite3, json

bp = Blueprint('dance', __name__, url_prefix='/dance')

@bp.route('/edit', methods=['GET', 'POST'])
def add_dance():
    db = get_db()

    if request.method == 'POST':
        data = json.loads(request.form['dance_data'])
        dance_name = data.get('danceName', 'Untitled Dance')
        source = data.get('source', '')
        video = data.get('video', '')
        steps = data.get('steps', [])

        cursor = db.execute(
            "INSERT INTO Dance (DanceName, Video, Source) VALUES (?, ?, ?)",
            (dance_name, video, source)
        )
        dance_id = cursor.lastrowid

        for step in steps:
            step_name = step['stepName']
            cursor = db.execute(
                "INSERT INTO Steps (DanceID, StepName) VALUES (?, ?)",
                (dance_id, step_name,)
            )
            step_id = cursor.lastrowid

            for place, fig_name in enumerate(step['figures']):
                row = db.execute(
                    "SELECT ID FROM Figure WHERE Name = ?",
                    (fig_name,)
                ).fetchone()

                if row:
                    figure_id = row['ID']
                    db.execute(
                        "INSERT INTO FigureStep (StepsId, FigureId, Place) VALUES (?, ?, ?)",
                        (step_id, figure_id, place,)
                    )
                else:
                    print(f"Warning: figure not found: {fig_name}")
        db.commit()
        return redirect(url_for('dance.add_dance'))

    return render_template('dance/create_dance.html')

@bp.route('/create_figure', methods=['POST'])
def create_figure():
    data = request.get_json() or {}
    db = get_db()

    name = data['name']
    roles = data['roles']
    start_pos = data['start_position']
    action = data['action']
    end_pos = data['end_position']
    duration = data['duration']

    cursor = db.execute(
        """
        INSERT INTO Figure
            (Name, Roles, StartPosition, Action, EndPosition, Duration)
            VALUES (?, ?, ?, ?, ?, ?) 
        """,
        (name, roles, start_pos, action, end_pos, duration)
    )
    new_id = cursor.lastrowid

    db.execute(
        """
        INSERT INTO FigureFTS(rowid, Name, Roles, StartPosition, Action, EndPosition)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (new_id, name, roles, start_pos, action, end_pos)
    )
    db.commit()
    return jsonify({'id': new_id, 'name': name}), 201


@bp.route('/search', methods=['POST'])
def search_figures():
    raw = request.get_json().get('q', '').strip()
    if not raw:
        return jsonify([]), 200

    tokens = re.findall(r'\w+', raw)
    if not tokens:
        return jsonify([]), 200

    param = " ".join(tok + "*" for tok in tokens)
    
    db = get_db()
    fts_sql = """
    SELECT F.ID, F.Name, F.Roles, F.StartPosition, F.Action, F.EndPosition, F.Duration,
        bm25(FigureFTS) AS score
    FROM FigureFTS
    JOIN Figure AS F on F.ID = FigureFTS.rowid
    WHERE FigureFTS MATCH ?
    ORDER BY score
    LIMIT 20;
    """
    try:
        rows = db.execute(fts_sql, (param,)).fetchall()
    except sqlite3.OperationalError:
        like = f"%{raw}%"
        fallback_sql = """
        SELECT ID,
               Name,
               Roles,
               StartPosition,
               Action,
               EndPosition,
               Duration
          FROM Figure
         WHERE Name LIKE ?
            OR Roles LIKE ?
            OR StartPosition LIKE ?
            OR Action LIKE ?
            OR EndPosition LIKE ?
         LIMIT 20;
        """
        rows = db.execute(fallback_sql, (like,)*5).fetchall()
    
    results = [
        {
            'id': r['ID'],
            'name': r['Name'],
            'roles': r['Roles'],
            'start_position': r['StartPosition'],
            'action': r['Action'],
            'end_position': r['EndPosition'],
            'duration': r['Duration']
        }
        for r in rows
    ]
    return jsonify(results), 200