from flask import (Blueprint, render_template, redirect, url_for, request, jsonify, current_app, abort)
from .db import get_db
import secrets, re, sqlite3, json
from collections import defaultdict

bp = Blueprint('dance', __name__, url_prefix='/dance')

@bp.route('/edit/<int:dance_id>', methods=['GET', 'POST'])
def edit_dance(dance_id):
    db = get_db()

    if request.method == 'POST':
        data       = json.loads(request.form['dance_data'])
        new_name   = data['danceName']
        new_video  = data['video']
        new_source = data['source']
        new_steps  = data['steps'] 

        db.execute(
          "UPDATE Dance SET DanceName=?, Video=?, Source=? WHERE ID=?",
          (new_name, new_video, new_source, dance_id)
        )

        db.execute(
          "DELETE FROM FigureStep "
          " WHERE StepsId IN (SELECT ID FROM Steps WHERE DanceID=?)",
          (dance_id,)
        )
        db.execute("DELETE FROM Steps WHERE DanceID=?", (dance_id,))

        for step in new_steps:
            cur = db.execute(
              "INSERT INTO Steps (DanceID, StepName) VALUES (?, ?)",
              (dance_id, step['stepName'])
            )
            step_id = cur.lastrowid

            for place, fig_name in enumerate(step['figures']):
                row = db.execute(
                  "SELECT ID FROM Figure WHERE Name = ?",
                  (fig_name,)
                ).fetchone()
                if row:
                    db.execute(
                      "INSERT INTO FigureStep (StepsId, FigureId, Place) "
                      "VALUES (?, ?, ?)",
                      (step_id, row['ID'], place)
                    )
                else:
                     current_app.logger.warning(f"Figure not found: {fig_name}")

        db.commit()
        return redirect(url_for('dance.edit_dance', dance_id=dance_id))

    dance_row = db.execute(
        "SELECT ID, DanceName, Video, Source FROM Dance WHERE ID = ?",
        (dance_id,)
    ).fetchone()
    if dance_row is None:
        abort(404)

    dance_data = {
        "danceID": dance_row["ID"],
        "danceName": dance_row["DanceName"],
        "video": dance_row["Video"],
        "source": dance_row["Source"],
        "steps": []
    }

    step_rows = db.execute(
        "SELECT ID, StepName FROM Steps WHERE DanceID = ? ORDER BY ID",
        (dance_id,)
    ).fetchall()

    for step in step_rows:
        fig_rows = db.execute(
            """
            SELECT F.Name
              FROM FigureStep FS
              JOIN Figure F ON FS.FigureId = F.ID
             WHERE FS.StepsId = ?
             ORDER BY FS.Place
            """,
            (step["ID"],)
        ).fetchall()

        dance_data["steps"].append({
            "stepName": step["StepName"],
            "figures":  [f["Name"] for f in fig_rows]
        })

    return render_template(
        'dance/manage_dance.html',
        dance=dance_data
    )

@bp.route('/create', methods=['GET', 'POST'])
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

    return render_template('dance/manage_dance.html')

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

@bp.route('/<int:dance_id>', methods=['GET', 'POST'])
def display_information(dance_id):
    db = get_db()

    # Get main dance information
    dance_info = db.execute(
        '''SELECT ID, DanceName, Video, Source 
           FROM Dance WHERE ID = ?''',
        (dance_id,)
    ).fetchone()

    if not dance_info:
        return "Dance not found", 404

    # Get steps and figures for this dance
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
        JOIN FigureStep fs ON fs.StepId = s.ID
        JOIN Figure f ON f.ID = fs.FigureId
        WHERE s.DanceId = ?
        ORDER BY s.StepName, fs.Place ASC
        ''', (dance_id,)
    ).fetchall()

    # Prepare the data for rendering
    steps = defaultdict(list)
    figures = {}

    for s in steps_and_figures:
        current_step = s['step_name']
        current_figure_id = s['figure_id']
        current_figure_name = s['figure_name']

        # Store figure details if not already stored
        if current_figure_id not in figures:
            figures[current_figure_id] = {
                'name': current_figure_name,
                'duration': s['duration'],
                'start_position': s['start_position'],
                'end_position': s['end_position'],
                'action': s['action']
            }

        # Append figure ID to the appropriate step
        steps[current_step].append(current_figure_id)

    return render_template('specific_dance.html', dance=dance_info, steps=steps, figures=figures)