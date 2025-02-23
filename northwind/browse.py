from flask import Blueprint, render_template, request
from northwind.db import get_db

bp = Blueprint('index', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    selected_category = None
    search_query = None
    items = []

    if request.method == 'POST':
        selected_category = request.form.get('category')
        search_query = request.form.get('search')

        if search_query:
            items = db.execute(
                'SELECT ProductName, UnitPrice, QuantityPerUnit '
                'FROM Product '
                'WHERE ProductName LIKE ? COLLATE NOCASE',
                (f"%{search_query}%",)
            ).fetchall()

            if not items:
                items = db.execute(
                    'SELECT ProductName, UnitPrice, QuantityPerUnit '
                    'FROM Product p '
                    'JOIN Category c ON p.CategoryID = c.Id '
                    'WHERE c.CategoryName LIKE ? COLLATE NOCASE',
                    (f"%{search_query}%",)
                ).fetchall()

            if not items:
                return render_template('search-error.html', search_query=search_query)

        elif selected_category and selected_category != 'All':
            items = db.execute(
                'SELECT ProductName, UnitPrice, QuantityPerUnit '
                'FROM Product p '
                'JOIN Category c ON p.CategoryID = c.Id '
                'WHERE c.CategoryName = ? '
                'ORDER BY ProductName',
                (selected_category,)
            ).fetchall()
        else:
            items = db.execute(
                'SELECT ProductName, UnitPrice, QuantityPerUnit '
                'FROM Product '
                'ORDER BY ProductName'
            ).fetchall()

    categories = db.execute('SELECT DISTINCT CategoryName FROM Category').fetchall()

    return render_template('index.html', items=items, categories=categories, selected_category=selected_category, search_query=search_query)
