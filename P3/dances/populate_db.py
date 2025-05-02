import sqlite3
import json
import glob
import os

DANCE_DIR = './output'
FIGURE_FILE = os.path.join(DANCE_DIR, 'figure_library.json')
DANCE_GLOB = os.path.join(DANCE_DIR, 'ins_*.json')
DB_FILE = './dances/dances.sqlite'

def insert_figures(cursor, figure_data):
    for fig in figure_data:
        cursor.execute('''
            INSERT INTO Figure (Name, Roles, StartPosition, Action, EndPosition, Duration)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            fig['name'],
            fig['roles'],
            fig['start_position'],
            fig['action'],
            fig['end_position'],
            fig['duration']
        ))

def get_figure_id(cursor, name):
    cursor.execute('SELECT ID FROM Figure WHERE Name = ?', (name,))
    result = cursor.fetchone()
    return result[0] if result else None

def insert_dance_and_steps(cursor, dance_data, source_filename):
    video = dance_data.get('video') # None if doesn't exist
    cursor.execute('''
        INSERT INTO Dance (DanceName, Source, Video)
        VALUES (?, ?, ?)
    ''', (
        dance_data.get('title', 'Untitled'),
        source_filename,
        video
    ))
    dance_id = cursor.lastrowid # Get the ID of the last inserted row
    missing_sum = 0
    for step_name, figures in dance_data.get('phrases', {}).items():
        cursor.execute('''
            INSERT INTO Steps (DanceId, StepName)
            VALUES (?, ?)
        ''', (dance_id, step_name))
        step_id = cursor.lastrowid
        for place, fig_name in enumerate(figures):
            figure_id = get_figure_id(cursor, fig_name)
            if figure_id:
                try:
                    cursor.execute('''
                        INSERT INTO FigureStep (StepsId, FigureId, Place)
                        VALUES (?, ?, ?)
                    ''', (step_id, figure_id, place))
                except sqlite3.IntegrityError as e:
                    print(f"[UNIQUE FAIL] {e} — File: {source_filename}, Step: {step_name}, Figure: {fig_name}")
            else:
                print(f"Figure not found in DB: \"{fig_name}\" (from {source_filename})")
                missing_sum += 1
    return missing_sum

def main():
    with open(FIGURE_FILE, 'r') as f:
        figures = json.load(f)

    conn = sqlite3.connect(DB_FILE)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()
    try:
        insert_figures(cursor, figures)
        conn.commit()
        total_missing_figures = 0
        total_added_dances = 0
        total_missing_dances = 0
        for dance_path in glob.glob(DANCE_GLOB):
            with open(dance_path, 'r') as f:
                dance_data = json.load(f)
            print(f"Importing {dance_path}...")
            current_missing = insert_dance_and_steps(cursor, dance_data, os.path.basename(dance_path))
            if current_missing == 0:
                total_added_dances += 1
                conn.commit()
            else:
                total_missing_dances += 1
                conn.rollback()
            total_missing_figures += current_missing
        print(total_missing_figures, "Missing figures in total.")
        print(total_added_dances, "Dances imported successfully.")
        print(total_missing_dances, "Dances with missing figures, thus skipped.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
