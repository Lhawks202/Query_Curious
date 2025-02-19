import shutil
import os
import pytest
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from northwind import create_app, db
from northwind.db import get_db

TEST_DB = "test_northwind.sqlite"

@pytest.fixture(scope='function')
def app():
    shutil.copyfile('./northwind/northwind.sqlite', TEST_DB)

    app = create_app()
    app.config['DATABASE'] = TEST_DB

    with app.app_context():
        db.init_db()
        yield app
    os.remove(TEST_DB)

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def register(self, username='test', password='test'):
        return self._client.post(
            '/auth/register',
            data={'user_id': username, 'password': password}
        )

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'user_id': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


class SearchActions(object):
    def __init__(self, app):
        self._app = app

    def insert_supplier(self, company_name='TestSupplier'):
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Supplier (CompanyName) VALUES (?)", (company_name,))
            db.commit()
            return db.execute("SELECT Id FROM Supplier WHERE CompanyName = ?", (company_name,)).fetchone()[0]

    def insert_category(self, category_name='TestCategory'):
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Category (CategoryName) VALUES (?)", (category_name,))
            db.commit()
            return db.execute("SELECT Id FROM Category WHERE CategoryName = ?", (category_name,)).fetchone()[0]

    def insert_product(self, product_name='TestProduct', unit_price=10.0, category_id=1, supplier_id=1, discontinued=0):
        with self._app.app_context():
            db = get_db()
            db.execute("INSERT INTO Product (ProductName, UnitPrice, CategoryId, SupplierId, UnitsInStock, UnitsOnOrder, ReorderLevel, Discontinued) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (product_name, unit_price, category_id, supplier_id, 999, 999, 999, discontinued))
            db.commit()


@pytest.fixture
def auth(client):
    return AuthActions(client)


@pytest.fixture
def search(app):
    return SearchActions(app)