from northwind import create_app

def test_create_app_with_test_config():
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test',
        'DATABASE': 'test_northwind.sqlite'
    }
    app = create_app(test_config)
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test'
    assert app.config['DATABASE'] == 'test_northwind.sqlite'

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200