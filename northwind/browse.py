from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from northwind.auth import login_required
from northwind.db import get_db

bp = Blueprint('browse', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    selected_category = None

    if request.method == 'POST':
        selected_category = request.form.get('category')
    
    if selected_category and selected_category != 'All':
        items = db.execute(
        'SELECT ProductName, UnitPrice, QuantityPerUnit'
        ' FROM Product p '
        ' JOIN Categories c on p.CategoryID = c.Id'
        ' WHERE c.CategoryName = ?'
        ' ORDER BY ProductName',
        (selected_category,)
    ).fetchall()
    else:
        items = db.execute(
            'SELECT ProductName, UnitPrice, QuantityPerUnit'
            ' FROM Product'
            ' ORDER BY ProductName'
        ).fetchall()
    
    categories = db.execute('SELECT DISTINCT CategoryName FROM Categories').fetchall()

    return render_template('index.html', items=items, categories=categories, selected_category=selected_category)