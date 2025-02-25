from flask import g, session
from northwind.db import get_db

def test_product_page_get(client, app, search):
    with app.app_context():
        db = get_db()
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)

        # Simulate a GET request to the product page
        response = client.get(f'/product?product=TestProduct')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'TestProduct' in response_text
        assert '10.00' in response_text  # Assuming the UnitPrice is 10.00
        assert '999' in response_text  # Assuming the UnitsInStock is 999

def test_product_page_post(client, app, search):
    with app.app_context():
        db = get_db()
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)

        # Simulate a POST request to the product page
        response = client.post(f'/product?product=TestProduct', data={
            'product_id': product_id,
            'quantity': 2,
            'add': True
        })
        assert response.status_code == 200  # Assuming the POST request does not redirect
        response_text = response.data.decode('utf-8')
        assert 'TestProduct' in response_text
        assert '10.00' in response_text  # Assuming the UnitPrice is 10.00
        assert '999' in response_text  # Assuming the UnitsInStock is 999

def test_product_page_not_found(client, app):
    with app.app_context():
        # Simulate a GET request to the product page with a non-existent product
        response = client.get(f'/product?product=NonExistentProduct')
        assert response.status_code == 200, "Missing Checks for non-existent product"
        response_text = response.data.decode('utf-8')
        print(response_text)
        assert 'Product not found' in response_text, "Incorrect redirect for non-existent product"