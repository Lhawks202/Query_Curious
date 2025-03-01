import os
from flask import Flask, render_template
from typing import Any, Dict, Optional


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # need to store this in a .env file eventually
        DATABASE=os.path.join(app.root_path, './northwind.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import auth, cart, checkout
    app.register_blueprint(auth.bp)
    app.register_blueprint(cart.bp)
    app.register_blueprint(checkout.bp)

    from . import browse
    app.register_blueprint(browse.bp)
    app.add_url_rule('/', endpoint='index')

    from . import product
    app.register_blueprint(product.bp)

    return app
