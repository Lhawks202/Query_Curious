from flask import (Blueprint, render_template, request, g)
from northwind.db import get_db
from northwind.cart import get_cart, get_cart_items

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

def calc_cost(cart_items):
    total_cost = 0
    total_items = 0
    for item in cart_items:
        subtotal = item['UnitPrice'] * item['Quantity']
        n_items = item['Quantity']
        
        total_cost += subtotal
        total_items += n_items
    return total_items, total_cost

def copy_to_orders(db, cart, cart_items, total_cost, total_items):
    # create new order
    order_id = db.execute(
        "INSERT INTO Orders (UserID, TotalCost, NumItems) VALUES (?, ?, ?)", 
        (cart['UserID'], total_cost, total_items,)
    ).lastrowid
    # copy over all items
    for item in cart_items:
        db.execute("UPDATE Cart_Items SET CartID = NULL, OrderID = ? WHERE CartItemID = ?", (order_id, item['CartItemID'],))
    # delete entry from shopping cart
    db.execute("DELETE FROM Shopping_Cart WHERE CartID = ?", (cart['CartID'],))
    db.commit()

def delete_old_items(db, user_id):
    # delete any old items associated with an shopping cart
    db.execute("""
        DELETE FROM Cart_Items 
        WHERE CartID IN (
            SELECT sh.CartID 
            FROM Shopping_Cart sh 
            JOIN Cart_Items it ON sh.CartID = it.CartID 
            WHERE sh.UserID = ? AND it.AddedTimestamp < datetime('now', '-1 month')
        )
    """, (user_id,))
    # delete any old items associated with an order
    db.execute("""
        DELETE FROM Cart_Items 
        WHERE OrderID IN (
            SELECT ord.OrderID 
            FROM Orders ord 
            JOIN Cart_Items it ON ord.OrderID = it.OrderID 
            WHERE ord.UserID = ? AND it.AddedTimestamp < datetime('now', '-1 month')
        )
    """, (user_id,))
    db.commit()

def add_to_order(user_id):
    db = get_db()
    cart = get_cart(db)
    cart_items = get_cart_items(db, cart)
    total_items, total_cost = calc_cost(cart_items)
    copy_to_orders(db, cart, cart_items, total_cost, total_items)
    delete_old_items(db, user_id)
    return total_items, total_cost, cart_items


@bp.route('/', methods=('POST', 'GET'))
def checkout():
    if request.method == 'POST':
        if not g.user:
            # reroute to login/register
            db = get_db()
            cart = get_cart(db)
            cart_items = get_cart_items(db, cart)
            total_items, total_cost = calc_cost(cart_items)
            shipping = request.form['shipping']
            return render_template('checkout/checkout.html', num_items=total_items, total_amount=total_cost, cart_items=cart_items, shipping=shipping)
        user_id = g.user["UserID"]
        shipping = request.form['shipping']
        total_items, total_cost, cart_items = add_to_order(user_id)
        return render_template('checkout/checkout.html', num_items=total_items, total_amount=total_cost, cart_items=cart_items, shipping=shipping)
    else:
        user_id = g.user["UserID"]
        shipping = request.form['shipping']
        total_items, total_cost, cart_items = add_to_order(user_id)
        return render_template('checkout/checkout.html', num_items=total_items, total_amount=total_cost, cart_items=cart_items, shipping=shipping)




@bp.route('/shipping/', methods=('GET', 'POST'))
def shipping():
    if request.method == 'POST':
        pass
    db = get_db()
    cart = get_cart(db)
    cart_items = get_cart_items(db, cart)
    total_items, total_cost = calc_cost(cart_items)
    return render_template('checkout/shipping.html', num_items=total_items, total_amount=total_cost)