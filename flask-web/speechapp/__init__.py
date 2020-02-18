import os
import config
import pickle
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.exc as exc

from werkzeug.exceptions import HTTPException

db = SQLAlchemy()

def create_app(test_config = None):
    app = Flask(__name__, instance_relative_config=True)

    # app.jinja_env.trim_blocks = True
    # app.jinja_env.lstrip_blocks = True

    if test_config is None:
        # app.config.from_object('config.DevelopmentConfig')
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object(test_config)
    
    if not app.config['DEBUG']:
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True   
 
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(os.path.join(app.instance_path,"patients"))
    except OSError:
        pass

    '''Initialize database'''
    db.init_app(app)

    from . import models

    with app.app_context():
        try:
            try:
                db.create_all()
                print("Database created or initiated.")
            # checks if a server is activated
            except exc.SQLAlchemyError:
                print("Database server not available, bypassing..")
                pass
        # checks if server settings are available
        except AttributeError:
            print("Database settings not available, bypassing..")
            pass

    from . import upload, patients
    app.register_blueprint(upload.bp)
    app.register_blueprint(patients.bp)

    from . import errors
    app.register_error_handler(HTTPException,errors.handle_not_found)
    app.register_error_handler(413,errors.request_entity_too_large)


    @app.route("/home")
    def index():
        return render_template("index.html")

    return app