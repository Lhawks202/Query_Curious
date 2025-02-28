from northwind.db import get_db

def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Search' in response.data
    assert b'Select Category:' in response.data

def test_index_post_search(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.post('/', data={'form_type': 'search', 'search': 'TestProduct'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/search/?item=TestProduct'

def test_index_post_category(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.post('/categories/', data={'form_type': 'category', 'selected_category': 'TestCategory'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/categories/?selected_category=TestCategory'

def test_display_categories_get(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.get('/categories/?selected_category=TestCategory')
    assert response.status_code == 200
    assert b'Products in \"TestCategory\"' in response.data

def test_display_categories_post(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.post('/categories/', data={'form_type': 'category', 'selected_category': 'TestCategory'})
    assert response.status_code == 302
    assert b'<a href=\"/categories/?selected_category=TestCategory\">' in response.data
    response = client.post('/categories/', data={'form_type': 'category'})
    assert response.status_code == 200
    assert b'All Products' in response.data

def test_display_search_get(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.get('/search/?item=TestProduct')
    assert response.status_code == 200
    assert b'TestProduct' in response.data

def test_display_search_post(client, search):
    search.insert_supplier()
    search.insert_category()
    search.insert_product()
    response = client.post('/search/', data={'search': 'TestProduct'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/search/?item=TestProduct'
    response = client.post('/search/', data={'search': 'TestCategory'})
    assert response.status_code == 302
    assert response.headers['Location'] == '/search/?item=TestCategory'

def test_search_no_results(client):
    response = client.post('/search/', data={'search': 'NonExistent'})
    assert response.status_code == 302
    response = client.get('/search/?item=NonExistent')
    assert response.status_code == 200
    assert b'No products found' in response.data