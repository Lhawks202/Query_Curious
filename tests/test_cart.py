from flask import session
import re
from northwind.cart import get_cart, get_cart_items, get_units_in_stock, update_quantity
from northwind.db import get_db

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
            client.get('/cart/')
            cart = get_cart(db, user_id)
            assert cart is not None


def test_get_cart_session_id(client, app, cart):
    with app.app_context():
        db = get_db()
        session_id = "testtesttesttesttesttesttesttest"
        cart.insert_shopping_cart(session_id=session_id)
        with client:
            client.get('/cart/')
            cart = get_cart(db, session_id)
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

        units_in_stock = get_units_in_stock(db, cart_id)
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
            response = client.post('/cart/update-quantity', data={
                'item_id': cart_item_id,
                'quantity': 2,
                'increment': '+'
                })
            assert response.status_code == 302  # Redirect to view_cart
            
            # Access flashed messages from the session
            with client.session_transaction() as sess:
                flashed_messages = sess.get('_flashes', [])
                assert "Error updating item quantity." not in [msg for category, msg in flashed_messages]

            with app.app_context():
                updated_quantity = db.execute("SELECT Quantity FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchone()[0]
                assert updated_quantity == 3

                
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
            cart_items = db.execute("SELECT * FROM Cart_Items WHERE CartItemID = ?", (cart_item_id,)).fetchall()
            assert len(cart_items) == 0