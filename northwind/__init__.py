import os

from flask import Flask, render_template


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev', # need to store this in a .env file eventually
        DATABASE=os.path.join(app.root_path, './northwind.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    from . import db
    db.init_app(app)

    from . import auth, cart
    app.register_blueprint(auth.bp)
    app.register_blueprint(cart.bp)

    from . import browse
    app.register_blueprint(browse.bp)
    app.add_url_rule('/', endpoint='index')

    from . import product
    app.register_blueprint(product.bp)

    return app
