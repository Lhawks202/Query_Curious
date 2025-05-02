from flask import (Blueprint, render_template, session, redirect, url_for, flash, request)
from .db import get_db
import secrets

bp = Blueprint('create', __name__, url_prefix='/create')

@bp.route('/', methods=['GET'])
def add_dance():
    return render_template('create/create_dance.html')