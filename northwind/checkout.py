from flask import (Blueprint, render_template, request)
from northwind.db import get_db
from northwind.cart import get_cart, get_cart_items

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

# TODO: 
# At some predictable time, such as whenever the user completes the 
# checkout procedure, we could delete all entries in Shopping_Cart 
# older than, say, a month prior to the checkout.

def calc_cost(cart_items):
    total_cost = 0
    total_items = 0
    for item in cart_items:
        subtotal = item['UnitPrice'] * item['Quantity']
        n_items = item['Quantity']
        
        total_cost += subtotal
        total_items += n_items
    return total_items, total_cost

@bp.route('/', methods=('GET', 'POST'))
def checkout():
    if request.method == 'POST':
        pass

    db = get_db()
    cart = get_cart(db)
    cart_items = get_cart_items(db, cart)
    total_items, total_cost = calc_cost(cart_items)
    return render_template('checkout/checkout.html', num_items=total_items, total_amount=total_cost, cart_items=cart_items)

