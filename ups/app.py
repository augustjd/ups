#!./devenv/bin/python
from flask import Flask, request, g
from flask.json import JSONEncoder

from werkzeug.routing import BaseConverter, ValidationError

import datetime
import os
import logging
import uuid
import decimal
import pathlib

from isodate import datetime_isoformat, date_isoformat, parse_date
from isodate.isoerror import ISO8601Error
from slugify import slugify

from .extensions import bcrypt, login_manager, migrate, marshmallow, storage
from .log import log, bright, random_color, color
from .models import Version
from .settings import DevConfig, TestConfig
from .database import db
from .views import blueprint as views_blueprint


def create_app(config='dev'):
    """Create the application, registers blueprints and extensions, and returns it.

    :param config: A string to indicate which object to use; one of ('prod', 'dev', 'test')
    """
    config_object = {'dev': DevConfig, 'test': TestConfig}[config]

    app = Flask(__name__)
    app.config.from_object(config_object)

    if app.config.get('PROFILE'):
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    configure_log(app)
    configure_database(app)
    configure_json(app)
    configure_converters(app)

    register_extensions(app)
    register_blueprints(app)

    log.info("%s loaded with %s configuration", bright("ups"), bright(config))

    return app


def configure_log(app):
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        log.setLevel(logging.ERROR)
    elif app.config['DEBUG']:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    @app.before_request
    def request_log():
        g.request_start_time = datetime.datetime.now()
        g.request_tag = color(random_color(), request.remote_addr)
        log.info("%s     %s %s", g.request_tag, request.method, request.path)

    @app.after_request
    def response_log(response):
        response_time_ms = (datetime.datetime.now() - g.request_start_time).total_seconds() * 1000.0
        log.info("%s %d %s %s (in %.0fms)", g.request_tag,
                 response.status_code, request.method, request.path,
                 response_time_ms)

        return response


def configure_database(app):
    db.init_app(app)

    if app.config['TESTING'] or app.config['DEBUG']:
        with app.app_context():
            db.create_all()

    app.db = db

    migrate.init_app(app, db)


def configure_json(app):
    class CustomJSONEncoder(JSONEncoder):
        def __init__(self, *args, **kwargs):
            kwargs['separators'] = ',', ':'
            super().__init__(*args, **kwargs)

        def default(self, obj):
            try:
                if isinstance(obj, uuid.UUID):
                    return str(obj)
                elif isinstance(obj, decimal.Decimal):
                    return float(obj)
                elif isinstance(obj, datetime.datetime):
                    return datetime_isoformat(obj)
                elif isinstance(obj, datetime.date):
                    return date_isoformat(obj)
                elif isinstance(obj, pathlib.Path):
                    return str(obj)
                elif isinstance(obj, Version):
                    return str(obj)
                iterable = iter(obj)
            except TypeError:
                pass
            else:
                return list(iterable)
            return JSONEncoder.default(self, obj)

    app.json_encoder = CustomJSONEncoder


def configure_converters(app):
    class SlugConverter(BaseConverter):
        def to_python(self, value):
            return slugify(value)

        def to_url(self, value):
            return slugify(value)

    class DateConverter(BaseConverter):
        def to_python(self, value):
            try:
                return parse_date(value)
            except ISO8601Error:
                raise ValidationError()

        def to_url(self, value):
            return date_isoformat(value)

    class UUIDConverter(BaseConverter):
        def to_python(self, value):
            try:
                return uuid.UUID(value)
            except ValueError:
                raise ValidationError()

        def to_url(self, value):
            return str(value)

    class VersionConverter(BaseConverter):
        def to_python(self, value):
            try:
                return Version(value)
            except ValueError:
                raise ValidationError()

        def to_url(self, value):
            return str(value)

    app.url_map.converters['date'] = DateConverter
    app.url_map.converters['uuid'] = UUIDConverter
    app.url_map.converters['slug'] = SlugConverter
    app.url_map.converters['version'] = VersionConverter


def register_extensions(app):
    """Register Flask extensions."""
    bcrypt.init_app(app)
    login_manager.init_app(app)
    marshmallow.init_app(app)

    storage.init_app(app)
    app.storage = storage


def register_blueprints(app):
    app.register_blueprint(views_blueprint)
