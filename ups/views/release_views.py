from flask import request

from .responses import ReleaseNotFoundErrorResponse, SuiteNotFoundErrorResponse
from .blueprint import blueprint

from ups.models import (Release, release_manifest_schema, Suite)

from isodate import parse_datetime


def get_release(id):
    release = Release.get(id)

    if release is None:
        raise ReleaseNotFoundErrorResponse(id)

    return release


@blueprint.route('/releases/<id>', methods=['GET'])
def route_get_release(id):
    release = get_release(id)

    return release_manifest_schema.jsonify(release)


@blueprint.route('/releases/', methods=['POST'])
def route_create_release(id):
    d = request.get_json()

    title = None
    suite = None

    if isinstance(d, dict):
        if isinstance(d.get('title'), str):
            title = d['title']

        if isinstance(d.get('suite_id'), str):
            suite_id = d['suite_id']
            suite = Suite.get(suite_id)

            if suite is None:
                raise SuiteNotFoundErrorResponse(suite_slug=suite_id)

    release = Release(title=title, suite=suite)

    release.save()

    return release_manifest_schema.jsonify(release)


@blueprint.route('/releases/<id>/schedule', methods=['POST'])
def route_schedule_release(id):
    release = get_release(id)

    datetime = parse_datetime(request.get_json().get('datetime'))

    release.schedule(datetime, commit=True)

    return release_manifest_schema.jsonify(release)
