from flask import request

from .responses import ReleaseNotFoundErrorResponse
from .blueprint import blueprint

from ups.models import (Release, release_manifest_schema)

from isodate import parse_datetime


@blueprint.route('/releases/<id>', methods=['GET'])
def route_get_release(id):
    if id == 'current':
        release = Release.current()
    else:
        release = Release.get(id)

    if release is None:
        raise ReleaseNotFoundErrorResponse(id)

    return release_manifest_schema.jsonify(release)


@blueprint.route('/releases/<id>/schedule', methods=['POST'])
def route_schedule_release(id):
    if id == 'current':
        release = Release.current()
    else:
        release = Release.get(id)

    if release is None:
        raise ReleaseNotFoundErrorResponse(id)

    datetime = parse_datetime(request.get_json().get('datetime'))

    release.schedule(datetime, commit=True)

    return release_manifest_schema.jsonify(release)
