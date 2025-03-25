import sqlite3
from datetime import datetime

import click
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

    with current_app.open_resource('added_schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command() -> None:
    """Create new table(s)."""
    init_db()
    click.echo('Initialized Authentication table.')

def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)