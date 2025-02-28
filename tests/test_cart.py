import re
from flask import session
from northwind.cart import get_cart, get_cart_items, get_units_in_stock, create_cart
from northwind.db import get_db


def test_create_cart_session_id(client, app):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        with client.session_transaction() as sess:
            sess['session_id'] = session_id
        with client:
            client.get('/cart/')
            cart_id = create_cart(db)
            cart = db.execute("SELECT * FROM Shopping_Cart WHERE CartID = ?", (cart_id,)).fetchone()
            assert cart is not None
            assert cart['SessionID'] == session_id
            assert cart['UserID'] is None


def test_create_cart_user_id(client, app, auth):
    with app.app_context():
        db = get_db()
        auth.register()
        auth.login()
        session_id = "testtesttesttesttesttesttesttest"
        user_id = "testtestingauth"

        # Simulate a logged-in user by setting the user_id in the session
        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        with client:
            client.get('/cart/')
            cart_id = create_cart(db)
            cart = db.execute("SELECT * FROM Shopping_Cart WHERE CartID = ?", (cart_id,)).fetchone()
            assert cart is not None
            assert cart['SessionID'] == session_id
            assert cart['UserID'] == user_id


def test_get_session_id(client):
    with client:
        client.get('/cart/')
        assert 'session_id' in session
        session_id = session['session_id']
        assert len(session_id) == 32


def test_get_cart_user_id(client, app, auth, cart):
    with app.app_context():
        db = get_db()
        auth.register()
        auth.login()
        user_id = "test"
        cart.insert_shopping_cart(user_id=user_id)
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
            client.get('/cart/')
            cart = get_cart(db)
            assert cart is not None


def test_get_cart_session_id(client, app, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        cart.insert_shopping_cart(session_id=session_id)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            client.get('/cart/')
            cart = get_cart(db)
            assert cart is not None  
        

def test_get_cart_items(app, search, cart):
    with app.app_context():
        db = get_db()
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)

        cart = {'CartID': cart_id}
        cart_items = get_cart_items(db, cart)
        assert len(cart_items) == 1
        assert cart_items[0]['ProductName'] == 'TestProduct'
        assert cart_items[0]['Quantity'] == 2


def test_get_units_in_stock(app, search, cart):
    with app.app_context():
        db = get_db()
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)
        cart_item_id = db.execute("SELECT CartItemID FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()[0]
        units_in_stock = get_units_in_stock(db, cart_item_id)
        assert units_in_stock['UnitsInStock'] == 999


def test_view_cart(client, app, search, cart):
    with app.app_context():
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.get('/cart/')
            assert response.status_code == 200
            response_text = response.data.decode('utf-8')
            assert not re.search(r'Shopping Cart is empty.', response_text)


def test_update_quantity(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)
        cart_item_id = db.execute("SELECT CartItemID FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()[0]
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            # Test incrementing quantity
            response = client.post('/cart/update-quantity', data={
                'item_id': cart_item_id,
                'quantity': 2,
                'increment': 'true'
                })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." not in [msg for category, msg in flashed_messages]
            with app.app_context():
                updated_quantity = db.execute("SELECT Quantity FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchone()[0]
                assert updated_quantity == 3
            # Test decrementing quantity
            response = client.post('/cart/update-quantity', data={
                'item_id': cart_item_id,
                'quantity': 3,
                'decrement': 'true'
                })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." not in [msg for category, msg in flashed_messages]
            with app.app_context():
                updated_quantity = db.execute("SELECT Quantity FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchone()[0]
                assert updated_quantity == 2


def test_update_quantity_item_out_of_stock(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 999)
        cart_item_id = db.execute("SELECT CartItemID FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()[0]
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/update-quantity', data={
                'item_id': cart_item_id,
                'quantity': 999,
                'increment': 'true'
                })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." not in [msg for category, msg in flashed_messages]
                assert "Quantity Requested is not in Stock" in [msg for category, msg in flashed_messages]
            with app.app_context():
                updated_quantity = db.execute("SELECT Quantity FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchone()[0]
                assert updated_quantity == 999


def test_update_quantity_errors(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 999)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/update-quantity', data={
                'item_id': "FAKE",
                'quantity': 0,
                'increment': 'true'
                })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." in [msg for category, msg in flashed_messages]


def test_update_quantity_zero_items(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 1)
        cart_item_id = db.execute("SELECT CartItemID FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()[0]
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/update-quantity', data={
                'item_id': cart_item_id,
                'quantity': 1,
                'decrement': 'true'
                })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." not in [msg for category, msg in flashed_messages]
            with app.app_context():
                updated_quantity = db.execute("SELECT Quantity FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchone()[0]
                assert updated_quantity == 1, "Quantity should not be decremented below 1"


def test_remove_item(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)
        cart_item_id = db.execute("SELECT CartItemID FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()[0]
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/remove-item', data={'item_id': cart_item_id, 'remove': True})
            assert response.status_code == 302  # Redirect to view_cart
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error removing item." not in [msg for category, msg in flashed_messages]
            cart_items = db.execute("SELECT * FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchall()
            assert len(cart_items) == 0


def test_remove_item_errors(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        cart_id = cart.insert_shopping_cart()
        cart.insert_cart_items(cart_id, product_id, 2)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/remove-item', data={})
            assert response.status_code == 302  # Redirect to view_cart
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error removing item." in [msg for category, msg in flashed_messages]


def test_add_to_cart_no_cart(client, app, search):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            # Simulate adding an item to the cart
            response = client.post('/cart/add-to-cart', data={
                'product_id': product_id,
                'quantity': 2,
                'add': True
            })
            assert response.status_code == 302
            cart_id = db.execute("SELECT CartID FROM Shopping_Cart ORDER BY CartID DESC LIMIT 1").fetchone()[0]
            cart_item = db.execute("SELECT * FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()
            assert cart_item is not None
            assert cart_item['Quantity'] == 2


def test_add_to_cart_with_cart(client, app, search):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            client.get('/cart/')
            cart_id = create_cart(db)
            # Simulate adding an item to the cart
            response = client.post('/cart/add-to-cart', data={
                'product_id': product_id,
                'quantity': 2,
                'add': True
            })
            assert response.status_code == 302
            cart_id = db.execute("SELECT CartID FROM Shopping_Cart ORDER BY CartID DESC LIMIT 1").fetchone()[0]
            cart_item = db.execute("SELECT * FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (cart_id, product_id)).fetchone()
            assert cart_item is not None
            assert cart_item['Quantity'] == 2


def test_add_to_cart_invalid_form(client, app):
    with app.app_context():
        session_id = "testtesttesttesttesttesttesttest"
        with client:
            with client.session_transaction() as sess:
                sess['session_id'] = session_id
            response = client.post('/cart/add-to-cart', data={
                'product_id': '',
                'quantity': '',
                'add': True
            })
            assert response.status_code == 302
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error adding item to cart." in [msg for category, msg in flashed_messages]


def test_add_to_cart_existing_item(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        units_in_stock = 10
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id, units_in_stock=units_in_stock)
 
        session_cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(session_cart_id, product_id, 5)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id

        # Add the same item to the cart again, exceeding the stock
        response = client.post('/cart/add-to-cart', data={
            'product_id': product_id,
            'quantity': 10,
            'add': True
        })
        assert response.status_code == 302
        cart_item = db.execute("SELECT * FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (session_cart_id, product_id)).fetchone()
        assert cart_item is not None
        assert cart_item['Quantity'] == units_in_stock
        with client.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
            assert f"Only {units_in_stock} units in stock" in [msg for category, msg in flashed_messages]


def test_add_to_cart_existing_item_within_stock(client, app, search, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        units_in_stock = 10
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id, units_in_stock=units_in_stock)

        session_cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(session_cart_id, product_id, 5)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
        response = client.post('/cart/add-to-cart', data={
            'product_id': product_id,
            'quantity': 3,
            'add': True
        })
        assert response.status_code == 302
        cart_item = db.execute("SELECT * FROM Cart_Items WHERE CartID = ? AND ProductID = ?", (session_cart_id, product_id)).fetchone()
        assert cart_item is not None
        assert cart_item['Quantity'] == 8
        with client.session_transaction() as sess:
            flashed_messages = sess.get('_flashes', [])
            assert f"Only {units_in_stock} units in stock" not in [msg for category, msg in flashed_messages]


def test_assign_user_merge_carts(client, app, auth, cart, search):
    with app.app_context():
        db = get_db()
        user_id = "testtestingauth"
        session_id = "testtesttesttesttesttesttesttest"
        auth.register()
        auth.login()

        # Create a session cart
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        session_cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(session_cart_id, product_id, 2)

        user_cart_id = cart.insert_shopping_cart(user_id=user_id)
        cart.insert_cart_items(user_cart_id, product_id, 1)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        response = client.get('/cart/assign-user')
        assert response.status_code == 302

        merged_cart_items = db.execute("SELECT * FROM Cart_Items WHERE CartID = ?", (user_cart_id,)).fetchall()
    
        # Verify that the session cart items were merged into the user cart
        assert len(merged_cart_items) == 1, "Cart items were not merged, still two seperate cart items"
        assert merged_cart_items[0]['Quantity'] == 3

        # Verify that the session cart was deleted
        session_cart = db.execute("SELECT * FROM Shopping_Cart WHERE CartID = ?", (session_cart_id,)).fetchone()
        assert session_cart is None


def test_assign_user_no_user_cart(client, app, auth, cart, search):
    with app.app_context():
        db = get_db()
        user_id = "testtestingauth"
        session_id = "testtesttesttesttesttesttesttest"
        auth.register()
        auth.login()

        # Create a session cart
        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        session_cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(session_cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id

        response = client.get('/cart/assign-user')
        assert response.status_code == 302

        # Verify that the session cart was assigned to the user
        user_cart = db.execute("SELECT * FROM Shopping_Cart WHERE CartID = ?", (session_cart_id,)).fetchone()
        assert user_cart is not None
        assert user_cart['UserID'] == user_id


def test_assign_user_redirect(client, app, auth, cart, search):
    with app.app_context():
        db = get_db()
        user_id = "testtestingauth"
        session_id = "testtesttesttesttesttesttesttest"
        
        auth.register()
        auth.login()

        supplier_id = search.insert_supplier()
        category_id = search.insert_category()
        product_id = search.insert_product(supplier_id=supplier_id, category_id=category_id)
        session_cart_id = cart.insert_shopping_cart(session_id=session_id)
        cart.insert_cart_items(session_cart_id, product_id, 2)

        with client.session_transaction() as sess:
            sess['session_id'] = session_id
            sess['user_id'] = user_id
            sess['next'] = '/cart'

        response = client.get('/cart/assign-user')
        assert response.status_code == 302
        assert response.headers['Location'] == '/cart'