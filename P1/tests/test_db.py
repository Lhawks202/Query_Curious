import pytest
import sqlite3
from flask import g, Flask
from flask.testing import FlaskClient
from northwind.db import close_db, get_db
from click.testing import CliRunner

@pytest.fixture #Ensures a new db connection for each test.
def db_connection():
    conn = sqlite3.connect('test_northwind.sqlite')
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


def test_init_db(runner: CliRunner, db_connection: sqlite3.Connection) -> None:
    result = runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert 'Initialized Authentication table.\n' in result.output

    cursor = db_connection.cursor()

    # Check if the Authentication table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='Authentication';
    """)
    table = cursor.fetchone()
    assert table is not None, "Authentication table was not created"

    # Check if the Product table has an index on ProductName
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' AND name='idx_product_name';
    """)
    index = cursor.fetchone()
    assert index is not None, "Index 'idx_product_name' was not created"

    # Check if the Shopping_Cart table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='Shopping_Cart';
    """)
    table = cursor.fetchone()
    assert table is not None, "Shopping_Cart table was not created"

    # Check if the Cart_Items table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='Cart_Items';
    """)
    table = cursor.fetchone()
    assert table is not None, "Cart_Items table was not created"

    # Check if the Orders table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='Orders';
    """)
    table = cursor.fetchone()
    assert table is not None, "Orders table was not created"