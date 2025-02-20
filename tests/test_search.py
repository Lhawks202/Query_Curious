import re

def test_search_get(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Search' in response.data


def test_search_product(client, search):
    # Insert a supplier and a product into the database
    supplier_id = search.insert_supplier()
    search.insert_product(supplier_id=supplier_id)

    response = client.post('/', data={'search': 'TestProduct'})
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'TestProduct' in response_text
    assert re.search(r'<td>TestProduct</td>\s*<td>10\.00</td>', response_text), "Decimals Dropping in Unit Price"

def test_search_partial_matches(client, search):
    supplier_id = search.insert_supplier()
    search.insert_product(product_name="AmazingTestProduct", supplier_id=supplier_id)
    search.insert_product(product_name="TestOne", supplier_id=supplier_id)
    search.insert_product(product_name="AmazingTest", supplier_id=supplier_id)
    
    response = client.post('/', data={'search': 'Test'})
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'AmazingTestProduct' in response_text, "Partial match not allowed"
    assert 'TestOne' in response_text, "Partial match not allowed"
    assert 'AmazingTest' in response_text, "Partial match not allowed"


def test_search_category(client, search):
    supplier_id = search.insert_supplier()
    category_id = search.insert_category()
    search.insert_product(supplier_id=supplier_id, category_id=category_id)

    response = client.post('/', data={'search': 'TestCategory'})
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'TestProduct' in response_text
    assert re.search(r'<td>TestProduct</td>\s*<td>10\.00</td>', response_text), "Decimals Dropping in Unit Price"


def test_search_no_results(client):
    response = client.post('/', data={'search': 'NonExistent'})
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Product not found' in response_text