def test_product_page_get(client, app, search):
    with app.app_context():
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        search.insert_product(supplier_id=supplier_id, category_id=category_id)

        response = client.get(f'/product?product=TestProduct')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'TestProduct' in response_text
        assert '10.00' in response_text 
        assert '999' in response_text  


def test_product_page_post(client, app, search):
    with app.app_context():
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)

        response = client.post(f'/product?product=TestProduct', data={
            'product_id': product_id,
            'quantity': 2,
            'add': True
        })
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'TestProduct' in response_text
        assert '10.00' in response_text 
        assert '999' in response_text  


def test_product_page_not_found(client, app):
    with app.app_context():
        response = client.get(f'/product?product=NonExistentProduct')
        assert response.status_code == 200, "Missing Checks for non-existent product"