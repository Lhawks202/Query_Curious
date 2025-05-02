import sqlite3
import json
import glob
import os

DANCE_DIR = '../output'
FIGURE_FILE = '../output/figure_library.json'
DANCE_GLOB = os.path.join(DANCE_DIR, 'ins_*.json')
DB_FILE = './dances.db'

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

    for step_name, figures in dance_data.get('phrases', {}).items():
            cursor.execute('''
                INSERT INTO Steps (DanceId, StepName)
                VALUES (?, ?)
            ''', (dance_id, step_name))
            step_id = cursor.lastrowid
            for place, fig_name in enumerate(figures):
                figure_id = get_figure_id(cursor, fig_name)
                if figure_id:
                    cursor.execute('''
                        INSERT INTO FigureStep (StepId, FigureId, Place)
                        VALUES (?, ?, ?)
                    ''', (step_id, figure_id, place))
                else:
                    print(f"Figure not found in DB: \"{fig_name}\" (from {source_filename})")

def main():
    with open(FIGURE_FILE, 'r') as f:
        figures = json.load(f)

    conn = sqlite3.connect(DB_FILE)
    conn.execute('PRAGMA foreign_keys = ON')
    cursor = conn.cursor()

    try:
        insert_figures(cursor, figures)

        for dance_path in glob.glob(DANCE_GLOB):
            with open(dance_path, 'r') as f:
                dance_data = json.load(f)
            print(f"Importing {dance_path}...")
            insert_dance_and_steps(cursor, dance_data, os.path.basename(dance_path))

        conn.commit()
        print("All dances imported successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()
