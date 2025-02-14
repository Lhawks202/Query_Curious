from flask import (Blueprint, render_template)

bp = Blueprint('cart', __name__, url_prefix='/cart')

@bp.route('/')
def view_cart():
    return render_template('cart/cart.html')