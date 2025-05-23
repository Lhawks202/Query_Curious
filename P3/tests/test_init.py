from dances import create_app

def test_create_app_with_test_config() -> None:
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test',
        'DATABASE': 'test_dances.sqlite'
    }
    app = create_app(test_config)
    assert app.config['TESTING'] is True
    assert app.config['SECRET_KEY'] == 'test'
    assert app.config['DATABASE'] == 'test_dances.sqlite'

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200