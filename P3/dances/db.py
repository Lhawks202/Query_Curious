import click
import subprocess
import sqlite3
import os
from flask import current_app, g, Flask
from typing import Optional

def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e: Optional[Exception] = None) -> None:
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db() -> None:
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def is_db_empty(database_path: str) -> bool:
    if not os.path.exists(database_path):
        return True
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='Dance'")
        table_exists = cursor.fetchone()[0] > 0
        if not table_exists:
            return True
        cursor.execute("SELECT COUNT(*) FROM Dance")
        return cursor.fetchone()[0] == 0
    except Exception as e:
        print(f"Could not check DB state: {e}")
        return False
    finally:
        conn.close()

@click.command('init-db')
@click.option('--populate', is_flag=True, help='Populate the database (without resetting) if empty.')
@click.option('--force', is_flag=True, help='Force reinitialization of the database before population.')
def init_db_command(populate: bool, force: bool) -> None:
    db_path = current_app.config['DATABASE']
    if force: # Deletes database and reinitializes
        click.echo('Forcing database reinitialization...')
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
                click.echo('Existing database deleted.')
        except OSError as e:
            click.echo(f'Error deleting database: {e}')
            return
    if not os.path.exists(db_path):
        init_db()
        click.echo('Initialized tables.')
    if populate:
        if is_db_empty(db_path):
            click.echo('Database is empty. Running populate_db.py...')
            try:
                subprocess.run(["python", "./dances/populate_db.py"], check=True)
                click.echo('Database populated.')
            except subprocess.CalledProcessError as e:
                click.echo(f'Failed to populate DB: {e}')
        else:
            click.echo('Database already populated. Skipping populate_db.py.')

def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)