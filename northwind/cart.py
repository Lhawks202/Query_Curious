from flask import (Blueprint, render_template, session, redirect, url_for, flash, request)
from northwind.db import get_db
import secrets
from .forms import (UpdateItemQuantity, RemoveItem, AddToCart)

bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_session_id():
    """Ensure a session_id exists in the session and return it."""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    print(session['session_id'])
    return session['session_id']

def create_cart(db):
    """Create a cart for the current session/user if it exists."""
    session_id = get_session_id()
    if 'user_id' in session:
        db.execute(
            "INSERT INTO Shopping_Cart (SessionID, UserID) VALUES (?, ?)",
            (session_id, session['user_id'],)
        )
    else:
        db.execute(
            "INSERT INTO Shopping_Cart (SessionID) VALUES (?)"
            (session_id,)
        )
    db.commit()
    cart_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    return cart_id


def get_cart(db):
    """Return the cart for the current session/user if it exists."""
    cart = None
    if 'user_id' in session:
        cart = db.execute(
            "SELECT CartID FROM Shopping_Cart WHERE UserID = ?",
            (session['user_id'],)
        ).fetchone()
    if cart is None:
        session_id = get_session_id()
        cart = db.execute(
            "SELECT CartID FROM Shopping_Cart WHERE SessionID = ?",
            (session_id,)
        ).fetchone()
    return cart

def get_cart_items(db, cart):
    """Return all items for a given cart."""
    cart_items = []
    if cart is not None:
        cart_items = db.execute(
            """
            SELECT ci.*, p.ProductName, p.UnitPrice
            FROM Cart_Items AS ci
            JOIN Product AS p ON ci.ProductId = p.Id
            WHERE ci.CartID = ?
            """,
            (cart['CartID'],)
        ).fetchall()
    return cart_items

def get_units_in_stock(db, item_id):
    units_in_stock = db.execute(
        """
        SELECT p.UnitsInStock
        FROM Cart_items as ci
        JOIN Product AS p ON ci.ProductID = p.Id
        WHERE ci.CartItemID = ?
        """,
        (item_id,)
    ).fetchone()
    return units_in_stock

@bp.route('/')
def view_cart():
    db = get_db()
    cart = get_cart(db)
    cart_items = get_cart_items(db, cart)
    
    cart_item_forms = []
    for cart_item in cart_items:
        update_quantity_form = UpdateItemQuantity()
        update_quantity_form.item_id.data = cart_item['CartItemID']
        update_quantity_form.quantity.data = int(cart_item['Quantity'])

        remove_item_form = RemoveItem()
        remove_item_form.item_id.data = cart_item['CartItemID']
        cart_item_forms.append([cart_item, update_quantity_form, remove_item_form])

    return render_template('cart/cart.html', cart=cart, cart_item_forms=cart_item_forms)

@bp.route('/update-quantity', methods=['POST'])
def update_quantity():
    form = UpdateItemQuantity()
    if not form.validate_on_submit():
        flash("Error updating item quantity.")
        return redirect(url_for('cart.view_cart'))

    db = get_db()
    item_id = form.item_id.data
    quantity = int(form.quantity.data)

    if form.increment.data:
        units_in_stock = get_units_in_stock(db, item_id)
        if quantity < units_in_stock['UnitsInStock']:
            quantity += 1
        else:
            flash("Quantity Requested is not in Stock")
    elif form.decrement.data and quantity > 1:
        quantity -= 1

    db.execute(
        "UPDATE Cart_Items SET Quantity = ? WHERE CartItemID = ?",
        (quantity, item_id)
    )
    db.commit()
    return redirect(url_for('cart.view_cart'))

@bp.route('/remove-item', methods=['POST'])
def remove_item():
    form = RemoveItem()
    if not form.validate_on_submit():
        flash("Error removing item.")
        return redirect(url_for('cart.view_cart'))
    
    db = get_db()
    item_id = form.item_id.data

    if form.remove.data:
        db.execute(
            "DELETE FROM Cart_Items WHERE CartItemID = ?",
            (item_id,)
        )
        db.commit()

    return redirect(url_for('cart.view_cart'))

@bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    form = AddToCart()
    if not form.validate_on_submit():
        flash("Error adding item to cart.")
        return redirect(url_for('search.search'))
    
    db = get_db()
    product_id = form.product_id.data
    quantity = form.quantity.data

    if form.add.data:
        cart = get_cart(db)
        if not cart:
            cart_id = create_cart(db)
        else:
            cart_id = cart['CartID']

        db.execute(
            "INSERT INTO Cart_Items (CartID, ProductID, Quantity) VALUES (?, ?, ?)",
            (cart_id, product_id, quantity,)
        )
        db.commit()
    # Need to Confirm with Katie that this is the Proper URL
    return redirect(url_for('search.search'))

