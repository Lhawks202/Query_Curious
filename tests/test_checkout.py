from flask import g, session, Flask
from flask.testing import FlaskClient
from northwind.db import get_db
from northwind.checkout import calc_cost
from typing import Any

def test_calc_cost() -> None:
    cart_items = [
        {'UnitPrice': 10.00, 'Quantity': 2},
        {'UnitPrice': 5.00, 'Quantity': 3},
    ]
    total_items, total_cost = calc_cost(cart_items)
    assert total_items == 5
    assert total_cost == 35.00


def test_checkout_get(client: FlaskClient, app: Flask, auth: Any, search: Any, cart: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id

        response = client.get('/checkout/')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<h1>Checkout</h1>' in response_text
        assert 'Cart Total: $20.00' in response_text


def test_checkout_post(client: FlaskClient, app: Flask, auth: Any, search: Any, cart: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id

        response = client.post('/checkout/?shipping=United+Package')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        print(response_text)
        assert '<h1>Checkout</h1>' in response_text
        assert 'Cart Total: $20.00' in response_text
        assert 'Shipping: United Package' in response_text


def test_checkout_post_not_logged_then_logged(client: FlaskClient, app: Flask, auth: Any, search: Any, cart: Any) -> None:
    with app.app_context():
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id

        response = client.post('/checkout/?shipping=United+Package')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<h1>Checkout</h1>' in response_text
        assert 'Subtotal for 2 Item(s): $20' in response_text

        auth.register()
        auth.login()
        response = client.get('/checkout/')
        response_text = response.data.decode('utf-8')
        print(response_text)
        assert 'Cart Total: $20.00' in response_text
        assert 'Shipping: United Package' in response_text, 'Shipping not saved on login'


def test_shipping_get(client: FlaskClient) -> None:
    response = client.get('/checkout/shipping/')
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Shipping' in response_text


def test_shipping_post(client: FlaskClient) -> None:
    response = client.post('/checkout/shipping/', data={'shipping_method': 'United Package'})
    assert response.status_code == 200
    response_text = response.data.decode('utf-8')
    assert 'Shipping' in response_text


# TODO: 
# Add check for the removal of old carts on checkout once writted.