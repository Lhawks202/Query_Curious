from flask import (Blueprint, render_template)
from northwind.db import get_db

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@bp.route('/')
def checkout():
    return render_template('checkout/checkout.html')