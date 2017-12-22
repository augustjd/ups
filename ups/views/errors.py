from flask import current_app, Response

import json
import jsonschema

from .blueprint import blueprint


RESPONSE_SCHEMA = json.load(open('./schemas/response.json'))


class ErrorResponse(Exception):
    def __init__(self, errors=[], status=500):
        indent = None
        separators = (',', ':')

        if current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] or current_app.debug:
            indent = 2
            separators = (', ', ': ')

        if type(errors) is str:
            error = {"detail": errors, "status": status}
            errors = [error]
        elif type(errors) is dict:
            error = errors
            error['status'] = status
            errors = [error]
        elif type(errors) is list and all(isinstance(e, ErrorResponse) for e in
                                          errors):
            errors = [e.errors for e in errors]

        response = {"errors": errors}

        jsonschema.validate(RESPONSE_SCHEMA, response)

        self.errors = errors

        self.response = Response(response=json.dumps(response,
                                                     indent=indent,
                                                     separators=separators),
                                 mimetype='application/json',
                                 status=status)


@blueprint.errorhandler(ErrorResponse)
def handle_error_response(error_response):
    return error_response.response


class JsonApiErrorResponse(ErrorResponse):
    def __init__(self, code=None, title=None, detail=None, status=500):
        error = {"status": status}

        if code:
            error['code'] = code

        if title:
            error['title'] = title

        if detail:
            error['detail'] = detail

        super().__init__(errors=error, status=status)


class ModelNotFoundErrorResponse(JsonApiErrorResponse):
    def __init__(self, model=None, model_name=None, id=None, detail=None, title=None, status=404):
        model_name = model_name or model.__name__

        if detail is None:
            if id is None:
                detail = f"No {model_name} found."
            else:
                detail = f"No {model_name} with id {id} found."

        super().__init__(
            code='not-found',
            title=title or f"{model_name} Not Found",
            detail=detail,
            status=status)


class ModelAlreadyExistsErrorResponse(JsonApiErrorResponse):
    def __init__(self, model=None, model_name=None, id=None, detail=None, status=400):
        model_name = model_name or model.__name__

        if detail is None:
            if id is None:
                detail = f"{model_name} already exists."
            else:
                detail = f"{model_name} with id {id} already exists."

        super().__init__(
            code='already-exists',
            title=f"{model_name} Already Exists",
            detail=detail,
            status=status)
