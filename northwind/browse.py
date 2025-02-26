from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, render_template_string
)
from northwind.db import get_db

bp = Blueprint('browse', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    selected_category = None
    search_query = None
    items = []
    categories = db.execute('SELECT CategoryName FROM Category').fetchall()

    if request.method == 'POST':
        form_type = request.form.get('form_type')

        if form_type == 'search':
            search_query = request.form.get('search')
            return redirect(url_for('browse.display_search', item=search_query))

        elif form_type == 'category':
            selected_category = request.form.get('selected_category')
            return redirect(url_for('browse.display_categories', selected_category=selected_category))
        else:
            items = db.execute(
                    'SELECT ProductName, UnitPrice, QuantityPerUnit '
                    'FROM Product '
                    'ORDER BY ProductName'
                ).fetchall()
    
    else:
        items = db.execute(
                'SELECT ProductName, UnitPrice, QuantityPerUnit '
                'FROM Product '
                'ORDER BY ProductName'
            ).fetchall()

    return render_template('index.html', items=items, categories=categories, selected_category=selected_category, search_query=search_query)

def browse_category(selected_category):
    db = get_db()
    if not selected_category or selected_category == 'All':
        items = db.execute(
            'SELECT ProductName, UnitPrice, QuantityPerUnit '
            'FROM Product '
            'ORDER BY ProductName'
        ).fetchall()
    else:
        items = db.execute(
                    'SELECT ProductName, UnitPrice, QuantityPerUnit '
                    'FROM Product p '
                    'JOIN Category c ON p.CategoryID = c.Id '
                    'WHERE c.CategoryName = ? '
                    'ORDER BY p.ProductName',
                    (selected_category,)
                ).fetchall()

    categories = db.execute('SELECT DISTINCT CategoryName FROM Category').fetchall()
    return items, categories

def search_product(item):
    db = get_db()
    product = db.execute(
            'SELECT ProductName, UnitPrice'
            ' FROM Product'
            ' WHERE ProductName LIKE ? COLLATE NOCASE', ('%' + item + '%',)
        ).fetchall()

    product_type = db.execute(
            'SElECT ProductName, UnitPrice'
            ' FROM Product, Category'
            ' WHERE CategoryName = ? COLLATE NOCASE'
            ' AND Category.id = Product.CategoryId ', (item,)
        ).fetchall()

    if not product and not product_type:
        return None
    if not product_type:
        return product
    return product_type

@bp.route('/categories/', methods=('GET', 'POST'))
def display_categories():
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'category':
            selected_category = request.form.get('selected_category')
            if selected_category:
                return redirect(url_for('browse.display_categories', selected_category=selected_category))

    selected_category = request.args.get('selected_category')   
    products, categories = browse_category(selected_category)
    return render_template('categories-display.html', products=products, selected_category=selected_category, categories=categories)

@bp.route('/search/', methods=('GET', 'POST'))
def display_search():
    if request.method == 'POST':
        item = request.form['search']
        if item:
            return redirect(url_for('browse.display_search', item=item))
        # want to reroute to a product page if clicked on product name
        # want to add to cart if clicked 'add to cart'
        
    # logic to display correct page
    item = request.args.get('item', '')  # Get the query parameter
    product = search_product(item)
    db = get_db()
    categories = db.execute('SELECT DISTINCT CategoryName FROM Category').fetchall()
    if not product:
        flash("No products found.")
        product = []
    return render_template('search-display.html', products=product, categories=categories)