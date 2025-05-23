import os, sqlite3
from flask import Flask, render_template
from typing import Any, Dict, Optional


def create_app(test_config: Optional[Dict[str, Any]] = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.root_path, './dances.sqlite'),
    )

    def parse_timestamp(value):
        """Custom timestamp parser."""
        return value.decode('utf-8') if value else None

    # Register the custom timestamp converter
    sqlite3.register_converter("timestamp", parse_timestamp)

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

    from . import auth
    app.register_blueprint(auth.bp)

    from . import dance
    app.register_blueprint(dance.bp)

    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule('/', endpoint='index')

    from . import learn
    app.register_blueprint(learn.bp)
    
    from . import profile
    app.register_blueprint(profile.bp)

    @app.route('/')
    def index():
        return render_template('index.html')


    return app