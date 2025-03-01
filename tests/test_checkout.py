from flask import g, session, Flask
from flask.testing import FlaskClient
from northwind.db import get_db
from northwind.checkout import calc_cost, copy_to_orders, delete_old_items
from northwind.cart import get_cart, get_cart_items
from typing import Any

def test_calc_cost() -> None:
    cart_items = [
        {'UnitPrice': 10.00, 'Quantity': 2},
        {'UnitPrice': 5.00, 'Quantity': 3},
    ]
    total_items, total_cost = calc_cost(cart_items)
    assert total_items == 5
    assert total_cost == 35.00

def test_shipping_get(client: FlaskClient, auth: Any, app: Flask) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        response = client.get('/checkout/shipping/')
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'Shipping Method' in response_text


def test_shipping_post(client: FlaskClient, auth: Any, app: Flask) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        response = client.post('/checkout/shipping/', data={'shipping_method': 'United Package'})
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert 'Shipping' in response_text


def test_copy_to_orders(client: FlaskClient, app: Flask, search: Any, cart: Any, auth: Any) -> None:
    with app.app_context():
        db = get_db()
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        user_id = "testtestingauth"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id_one = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        product_id_two = search.insert_product(supplier_id=supplier_id, category_id=category_id, product_name="TestProductTwo")
        cart_id = cart.insert_shopping_cart(session_id=session_id, user_id=user_id)
        cart.insert_cart_items(cart_id, product_id_one, 2)
        cart.insert_cart_items(cart_id, product_id_two, 4)
        
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
                sess['user_id'] = user_id
            client.get('/cart/')
            cart = get_cart(db)
            cart_items = get_cart_items(db, cart)
            total_items, total_cost = calc_cost(cart_items)

        copy_to_orders(db, {'CartID': cart_id, 'UserID': user_id}, cart_items, total_cost, total_items)

        # Verify that the order was created
        order = db.execute("SELECT * FROM Orders WHERE UserID = ?", (user_id,)).fetchone()
        assert order is not None
        assert order['TotalCost'] == total_cost
        assert order['NumItems'] == total_items
        assert order['OrderID'] is not None

        # Verify that the cart items were updated
        cart_items = db.execute("SELECT * FROM Cart_Items WHERE OrderID = ?", (order['OrderID'],)).fetchall()
        assert len(cart_items) == 2

        # Verify that the shopping cart was deleted
        cart = db.execute("SELECT * FROM Shopping_Cart WHERE CartID = ?", (cart_id,)).fetchone()
        assert cart is None


def test_delete_old_items(client: FlaskClient, app: Flask, search: Any, cart: Any, auth: Any) -> None:
    with app.app_context():
        db = get_db()
        auth.register()
        auth.login()
        user_id = "testtestingauth"
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id, user_id=user_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        # Add old items to the cart
        db.execute("UPDATE Cart_Items SET AddedTimestamp = datetime('now', '-2 months') WHERE CartID = ?", (cart_id,))
        db.commit()

        delete_old_items(db, user_id)

        # Verify that old items were deleted
        cart_items = db.execute("SELECT * FROM Cart_Items WHERE CartID = ?", (cart_id,)).fetchall()
        assert len(cart_items) == 0


def test_checkout_post(client: FlaskClient, app: Flask, search: Any, cart: Any, auth: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        user_id = "testtestingauth"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id, user_id=user_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        response = client.post('/checkout/', data={'shipping': 'United Package'})
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<h1>Checkout</h1>' in response_text
        assert 'Cart Total: $20.00' in response_text
        assert 'Shipping: United Package' in response_text


def test_checkout_post_logged_in(client: FlaskClient, app: Flask, search: Any, cart: Any, auth: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        user_id = "testtestingauth"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id, user_id=user_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        with app.test_request_context():
            g.user = get_db().execute(
                'SELECT * FROM Authentication WHERE UserID = ?', (user_id,)
            ).fetchone()

        response = client.post('/checkout/', data={'UserID': user_id, 'shipping': 'United Package'})
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<h1>Checkout</h1>' in response_text
        assert 'Cart Total: $20.00' in response_text
        assert 'Shipping: United Package' in response_text


def test_checkout_post_not_logged_in(client: FlaskClient, app: Flask, search: Any, cart: Any) -> None:
    with app.app_context():
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id

        response = client.post('/checkout/', data={'shipping': 'United Package'})
        assert response.status_code == 200  # Redirect to login


def test_checkout_get_logged_in(client: FlaskClient, app: Flask, search: Any, cart: Any, auth: Any) -> None:
    with app.app_context():
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        user_id = "testtestingauth"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id, user_id=user_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        response = client.post('/checkout/', data={'shipping': 'United Package'})
        assert response.status_code == 200
        response_text = response.data.decode('utf-8')
        assert '<h1>Checkout</h1>' in response_text
        assert 'Cart Total: $20.00' in response_text
        assert 'Shipping: United Package' in response_text


def test_checkout_get_not_logged_in(client: FlaskClient, app: Flask, search: Any, cart: Any) -> None:
    with app.app_context():
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
        response = client.post('/checkout/', data={'shipping': 'United Package'})
        assert response.status_code == 200