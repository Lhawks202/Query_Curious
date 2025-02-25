from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, render_template_string
)

from .forms import AddToCart

from northwind.db import get_db

bp = Blueprint('product', __name__)

@bp.route('/product', methods=('GET', 'POST'))
def product_page():
    if request.method == 'POST':
        pass
    form = AddToCart()
    
    db = get_db()
    product_name = request.args.get('product', '')  # Get the query parameter
    product = db.execute(
            'SELECT ProductName, Id, UnitPrice, QuantityPerUnit, UnitsInStock, Discontinued'
            ' FROM Product'
            ' WHERE ProductName = ? COLLATE NOCASE', (product_name,)
        ).fetchone()
    form.product_id.data = product['Id']
    if product is None:
        return render_template('/search-display.html')
    return render_template('display-product.html', product=product, form=form)