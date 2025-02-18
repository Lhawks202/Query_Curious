from flask import (Blueprint, render_template, session)
from northwind.db import get_db
import secrets

bp = Blueprint('cart', __name__, url_prefix='/cart')

def get_session_id():
    """Ensure a session_id exists in the session and return it."""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    return session['session_id']

def get_cart(db, session_id):
    """Return the cart for the current session/user if it exists."""
    cart = None
    if 'user_id' in session:
        cart = db.execute(
            "SELECT CartID FROM Shopping_Cart WHERE UserID = ?",
            (session['user_id'],)
        ).fetchone()
    if cart is None:
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


@bp.route('/')
def view_cart():
    db = get_db()
    session_id = get_session_id()
    cart = get_cart(db, session_id)
    cart_items = get_cart_items(db, cart)

    return render_template('cart/cart.html', cart=cart, cart_items=cart_items)