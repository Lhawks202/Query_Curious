from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, render_template_string
)
from werkzeug.exceptions import abort

from northwind.db import get_db

bp = Blueprint('search', __name__)



@bp.route('/', methods=('GET', 'POST'))
def search():
    if request.method == 'POST':
        item = request.form['search']
        db = get_db()
        
        products = db.execute(
            'SELECT ProductName, UnitPrice'
            ' FROM Product'
            ' WHERE ProductName = ?', (item,)
        ).fetchall()

        product_type = db.execute(
            'SElECT ProductName, UnitPrice'
            ' FROM Product, Category'
            ' WHERE CategoryName = ? AND Category.id = Product.CategoryId', (item,)
        ).fetchall()
        if not products and not product_type:
            return render_template('search/search-error.html')
        if not product_type:
            return render_template('search/search-display.html', products=products)
        return render_template('search/search-display.html', products=product_type)
    else:
        return render_template('index.html')
    
