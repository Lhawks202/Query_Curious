import pytest
import sqlite3
import os
from flask import g, Flask, current_app
from flask.testing import FlaskClient
from dances.db import close_db, get_db
from click.testing import CliRunner

@pytest.fixture #Ensures a new db connection for each test.
def db_connection(app):
    with app.app_context():
        db_path = current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


def test_get_db(app: Flask) -> None:
    with app.app_context():
        db = get_db()
        assert db is not None, "Failed to get database connection"
        assert 'db' in g, "Database connection not stored in g"


def test_close_db(app: Flask) -> None:
    with app.app_context():
        db = get_db()
        assert db is not None, "Failed to get database connection"
        close_db()
        assert 'db' not in g, "Database connection not removed from g"

def test_init_db(app: Flask, runner: CliRunner, db_connection: sqlite3.Connection) -> None:
    with app.app_context():
        db_path = current_app.config['DATABASE']
        if os.path.exists(db_path):
            os.remove(db_path)
        result = runner.invoke(args=['init-db'])
        assert result.exit_code == 0
        assert 'Initialized tables.\n' in result.output
        cursor = db_connection.cursor()
        expected_tables = [
            'Dance',
            'Step',
            'Figure',
            'FigureStep',
            'User',
            'Learned',
            'Learning'
        ]
        for table_name in expected_tables:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?;
            """, (table_name,))
            table = cursor.fetchone()
            assert table is not None, f"Table '{table_name}' was not created"
    
def test_populate_db(app: Flask, runner: CliRunner, db_connection: sqlite3.Connection) -> None:
    with app.app_context():
        result = runner.invoke(args=['init-db', '--populate'])
        assert result.exit_code == 0
        assert 'Database populated.' in result.output or 'Database already populated.' in result.output
        cursor = db_connection.cursor()
        testing_tables = [
            'Dance',
            'Step',
            'Figure',
            'FigureStep'
        ]
        for table_name in testing_tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            assert count > 0, f"No {table_name}s were populated"

def test_force_reinitialize_db(app: Flask, runner: CliRunner) -> None:
    with app.app_context():
        db_path = current_app.config['DATABASE']
        assert os.path.exists(db_path), "Dummy database file was not created."
        result = runner.invoke(args=['init-db', '--force'])
        assert result.exit_code == 0, "init-db command failed with --force option."
        assert 'Forcing database reinitialization...' in result.output
        assert 'Existing database deleted.' in result.output
        assert 'Initialized tables.' in result.output
        assert os.path.exists(db_path), "Database file was not reinitialized."
