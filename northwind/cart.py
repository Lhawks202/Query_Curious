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
            "INSERT INTO Shopping_Cart (SessionID) VALUES (?)",
            (session_id,)
        )
    db.commit()
    cart_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    return cart_id

def get_cart_via_cart_item_id(db, item_id):
    """Return the cart given an item belonging to that cart."""
    return db.execute(
        "SELECT CartID FROM Cart_Items WHERE CartItemID = ?",
        (item_id,)
    ).fetchone()

def get_cart_via_session_id(db):
    """Return the cart for the current session if it exists."""
    session_id = get_session_id()
    return db.execute(
        "SELECT * FROM Shopping_Cart WHERE SessionID = ?",
        (session_id,)
    ).fetchone()

def get_cart_via_user_id(db):
    """Return the cart for the current user if it exists"""
    return db.execute(
        "SELECT * FROM Shopping_Cart WHERE UserID = ?",
        (session['user_id'],)
    ).fetchone()


def get_cart(db):
    """Return the cart for the current session/user if it exists."""
    cart = None
    if 'user_id' in session:
        cart = get_cart_via_user_id(db)
    if cart is None:
        cart = get_cart_via_session_id(db)
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

def get_units_in_stock_cart_item_id(db, item_id):
    """Return units in stock for a given item"""
    units_in_stock = db.execute(
        """
        SELECT p.UnitsInStock
        FROM Cart_items as ci
        JOIN Product AS p ON ci.ProductID = p.Id
        WHERE ci.CartItemID = ?
        """,
        (item_id,)
    ).fetchone()['UnitsInStock']
    return units_in_stock

def get_units_in_stock_product_id(db, product_id):
    return db.execute(
        "SELECT UnitsInStock FROM Product WHERE Id = ?",
        (product_id,)
    ).fetchone()['UnitsInStock']

def update_cart_totals(db, cart_id):
    """Recalculate NumItems and TotalCost for a Given Cart; Called when Merging session_cart with user_cart"""
    totals = db.execute(
        """
        SELECT SUM (Quantity) AS NumItems, SUM (Quantity * p.UnitPrice) AS TotalCost
        FROM Cart_Items AS ci
        JOIN Product as p ON ci.ProductID = p.Id
        WHERE CartID = ?
        """,
        (cart_id,)
    ).fetchone()

    num_items = totals['NumItems'] if totals['NumItems'] else 0
    total_cost = totals['TotalCost'] if totals['TotalCost'] else 0.0

    db.execute(
        "UPDATE Shopping_Cart SET NumItems = ?, TotalCost = ? WHERE CartID = ?",
        (num_items, total_cost, cart_id)
    )
    db.commit()

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
        units_in_stock = get_units_in_stock_cart_item_id(db, item_id)
        if quantity < units_in_stock:
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

    # Get the CartID associated with CartItemID
    cart = get_cart_via_cart_item_id(db, item_id)
    cart_id = cart['CartID']
    update_cart_totals(db, cart_id)

    return redirect(url_for('cart.view_cart'))

@bp.route('/remove-item', methods=['POST'])
def remove_item():
    form = RemoveItem()
    if not form.validate_on_submit():
        flash("Error removing item.")
        return redirect(url_for('cart.view_cart'))
    
    db = get_db()
    item_id = form.item_id.data

    cart = get_cart_via_cart_item_id(db, item_id)
    cart_id = cart['CartID']

    if form.remove.data:
        db.execute(
            "DELETE FROM Cart_Items WHERE CartItemID = ?",
            (item_id,)
        )
        db.commit()
    
    update_cart_totals(db, cart_id)

    return redirect(url_for('cart.view_cart'))

@bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    form = AddToCart()
    if not form.validate_on_submit():
        flash("Error adding item to cart.")
        return redirect(url_for('cart.view_cart'))
    
    db = get_db()
    product_id = form.product_id.data
    quantity = form.quantity.data
    units_in_stock = get_units_in_stock_product_id(db, product_id)

    if form.add.data:
        cart = get_cart(db)
        if not cart:
            cart_id = create_cart(db)
        else:
            cart_id = cart['CartID']

        existing_item = db.execute(
            "SELECT CartItemID, Quantity FROM Cart_Items WHERE CartID = ? AND ProductID = ?",
            (cart_id, product_id,)
        ).fetchone()

        if existing_item:
            quantity += existing_item['Quantity']
            if quantity > units_in_stock:
                flash(f"Only {units_in_stock} units in stock")
            quantity = quantity if quantity <= units_in_stock else units_in_stock
            db.execute(
                "UPDATE Cart_Items SET Quantity = ? WHERE CartItemID = ?",
                (quantity, existing_item['CartItemID'],)
            )
        else:
            if quantity > units_in_stock:
                flash(f"Only {units_in_stock} units in stock")
            quantity = quantity if quantity <= units_in_stock else units_in_stock
            db.execute(
                "INSERT INTO Cart_Items (CartID, ProductID, Quantity) VALUES (?, ?, ?)",
                (cart_id, product_id, quantity,)
            )
        db.commit()

        update_cart_totals(db, cart_id)
    return redirect(url_for('cart.view_cart'))

# @bp.route('/assign-user', methods=['GET', 'POST'])
# def assign_user():
#     db = get_db()
#     session_cart = get_cart_via_session_id(db)
#     user_cart = get_cart_via_user_id(db)
    
#     if session_cart:
#         if user_cart:
#             # The User has already their User Cart
#             # Need to Merge Current Session Cart with Existing User Cart
#             db.execute(
#                 "UPDATE Cart_Items SET CartID = ? WHERE CartID = ?",
#                 (user_cart['CartID'], session_cart['CartID'],)
#             )
#             db.execute(
#                 "DELETE FROM Shopping_Cart WHERE CartID = ?",
#                 (session_cart['CartID'],)
#             )

#             update_cart_totals(db, user_cart['CartID'])
#         else:
#             # The User has no Cart Yet
#             # Can Modify Existing Session Cart
#             db.execute(
#                 "UPDATE Shopping_Cart SET UserID = ? WHERE CartID = ? AND UserID IS NULL",
#                 (session['user_id'], session_cart['CartID'],)
#             )
#         db.commit()

#     next = session.pop('next', None)
#     if next:
#         return redirect(next)
#     return redirect(url_for('index'))

@bp.route('/assign-user', methods=['GET', 'POST'])
def assign_user():
    db = get_db()
    session_cart = get_cart_via_session_id(db)
    user_cart = get_cart_via_user_id(db)
    
    if session_cart:
        if user_cart:
            # Merge session cart items into the user's cart
            session_items = db.execute(
                "SELECT * FROM Cart_Items WHERE CartID = ?",
                (session_cart['CartID'],)
            ).fetchall()

            for item in session_items:
                # Check if this product already exists in the user's cart
                existing_item = db.execute(
                    "SELECT CartItemID, Quantity FROM Cart_Items WHERE CartID = ? AND ProductID = ?",
                    (user_cart['CartID'], item['ProductID'])
                ).fetchone()

                if existing_item:
                    # If it exists, add the quantities together
                    units_in_stock = get_units_in_stock_cart_item_id(db, existing_item['CartItemID'])
                    
                    quantity = existing_item['Quantity'] + item['Quantity']
                    if quantity > units_in_stock:
                        flash(f"Only {units_in_stock} units in stock")
                    quantity = quantity if quantity <= units_in_stock else units_in_stock
                    db.execute(
                        "UPDATE Cart_Items SET Quantity = ? WHERE CartItemID = ?",
                        (quantity, existing_item['CartItemID'])
                    )
                    # Remove the duplicate session cart item
                    db.execute(
                        "DELETE FROM Cart_Items WHERE CartItemID = ?",
                        (item['CartItemID'],)
                    )
                else:
                    # If the product does not exist in the user cart, simply reassign its CartID
                    db.execute(
                        "UPDATE Cart_Items SET CartID = ? WHERE CartItemID = ?",
                        (user_cart['CartID'], item['CartItemID'])
                    )
            db.execute(
                "DELETE FROM Shopping_Cart WHERE CartID = ?",
                (session_cart['CartID'],)
            )
            update_cart_totals(db, user_cart['CartID'])
        else:
            db.execute(
                "UPDATE Shopping_Cart SET UserID = ? WHERE CartID = ? AND UserID IS NULL",
                (session['user_id'], session_cart['CartID'])
            )
            update_cart_totals(db, session_cart['CartID'])
        db.commit()

    next = session.pop('next', None)
    if next:
        return redirect(next)
    return redirect(url_for('index'))
