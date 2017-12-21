from flask_login import current_user, login_required
from flask import jsonify, request

from ups.log import log

import functools
import os
import json
import pathlib
import jsonschema
import re

from isodate import parse_date


def success(data=None):
    """Return a success response."""
    return jsonify(data), 200


def fail(errors=[], status_code=500):
    """Return a failure response."""
    if type(errors) is str:
        error = {"detail": errors}
        error['status'] = status_code
        errors = [error]
    elif type(errors) is dict:
        error = errors
        error['status'] = status_code
        errors = [error]

    return jsonify(errors=errors), status_code


def role_required(role):
    def decorator(route):
        route = login_required(route)

        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            if current_user is None or current_user.is_anonymous or not current_user.has_role(role):
                return fail("You don't have permission to do this.", 401)

            return route(*args, **kwargs)

        return decorated_route

    return decorator


def concerns(Model, key=None, id_key="id", check_login=True):
    if key is None:
        key = Model.__tablename__

        # remove plural, if possible
        if key[-1] == 's':
            key = key[:-1]

    def decorator(route):
        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            if id_key not in kwargs:
                return fail("No id was provided.")

            model_name = Model.__tablename__

            try:
                model = Model.query.get(kwargs[id_key])
            except ValueError:
                log.exception("@concerns failed with input %s", kwargs[id_key])
            except Exception:
                log.exception("@concerns failed with input %s", kwargs[id_key])
                error = f"Server failed to lookup {model_name} with id {kwargs.get(id_key)}."
                return fail(error, 500)

            if model is None:
                return fail("No {} exists with id {}.".format(model_name, kwargs[id_key]), 404)

            del kwargs[id_key]
            kwargs[key] = model

            return route(*args, **kwargs)

        return decorated_route

    return decorator


def get_json_validator(schema):
    if type(schema) is str:
        try:
            schema = json.load(open(schema))
        except Exception:
            raise Exception(f'validate_request_json: failed to load JSON schema from {schema}')

    # get a properly formatted file:// path to the directory for schemas,
    # to allow schema reference resolution.
    # for some reason, pathlib.Path() does not append a / to a direcory,
    # so I put it in manually
    schemas_directory = os.path.abspath("./schemas/")
    schemas_directory_uri = pathlib.Path(schemas_directory).as_uri()
    schemas_directory_uri_string = str(schemas_directory_uri) + "/"

    resolver = jsonschema.RefResolver(schemas_directory_uri_string, schema)

    return jsonschema.Draft4Validator(schema, resolver=resolver,
                                      format_checker=jsonschema.FormatChecker())


MISSING_REQUIREMENT_REGEX = re.compile(r"^'(?P<key>.+)' is a required property$")


def error_dict_for_validation_error(error):
    """Construct a human-readable error dict for a JSON validation error."""
    if error.validator == 'required':
        try:
            key = MISSING_REQUIREMENT_REGEX.match(error.message).groupdict()['key']
            error.path.append(key)
        except Exception:
            error = "error_dict_for_validation_error: Failed to determine key \
                     of missing 'required' property."
            log.exception(error)

    error.path = [str(p) for p in error.path]

    return {'.'.join(error.path): error.message}


def validate_request_json(schema):
    """Augment a route by adding a JSON schema pass before route handling."""
    validator = get_json_validator(schema)

    def decorator(route):
        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            data = request.get_json()

            if data is None:
                error = {
                    "code": "json-required",
                    "title": "Request Requires JSON",
                    "detail": f"This route requires JSON data."
                }
                return fail(error, 400)

            errors = [error_dict_for_validation_error(e)
                      for e in validator.iter_errors(request.get_json())]

            if len(errors) > 0:
                return fail(errors, 400)

            return route(*args, **kwargs)

        return decorated_route

    return decorator


def limit_query(default=50, max=50):
    def limit_query_decorator(route):
        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            if 'limit' in request.args:
                try:
                    kwargs['limit'] = int(request.args['limit'])
                    if kwargs['limit'] > max:
                        return fail("'limit' must be <= {}".format(max), 400)

                except Exception:
                    return fail("Failed to parse 'limit' as an integer.", 400)
            else:
                kwargs['limit'] = default

            return route(*args, **kwargs)

        return decorated_route

    return limit_query_decorator


def date_range_query(route):
    @functools.wraps(route)
    def decorated_route(*args, **kwargs):
        if 'start' in request.args:
            try:
                kwargs['start'] = parse_date(request.args['start'])
            except Exception:
                return fail("Failed to parse 'start' as ISO8601 date.", 400)

        if 'end' in request.args:
            try:
                kwargs['end'] = parse_date(request.args['end'])
            except Exception:
                return fail("Failed to parse 'end' as ISO8601 date.", 400)

        return route(*args, **kwargs)

    return decorated_route


def validate_request_file(extension=None, key="file"):
    extensions = [extension] if type(extension) is str else extension

    def decorator(route):
        @functools.wraps(route)
        def decorated_route(*args, **kwargs):
            file = request.files.get(key)

            if file is None:
                if extensions:
                    return fail("Must provide a {} file.".format(extensions), 400)
                else:
                    return fail("Must provide a file.", 400)

            _, file_extension = os.path.splitext(file.filename)

            if file_extension not in extensions:
                return fail(f"Must provide a {extension} file (you gave {file_extension}).", 400)

            kwargs[key] = file

            return route(*args, **kwargs)

        return decorated_route

    return decorator
