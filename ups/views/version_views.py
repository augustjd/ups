import json

from .utils import success, fail
from .blueprint import blueprint
from .responses import (VersionNotFoundErrorResponse,
                        VersionAlreadyExistsErrorResponse,
                        InvalidArgumentResponse)

from flask import request

from ups.models import (PackageVersion, package_version_schema)

from .package_views import get_package


def get_version(package_slug, version):
    package = get_package(package_slug)

    version = package.versions.filter_by(version=version).first()

    if version is None:
        raise VersionNotFoundErrorResponse(version, package_slug)

    return version


@blueprint.route('/packages/<slug:package_slug>/<version:version>', methods=['GET'])
def route_get_version(package_slug, version):
    version = get_version(package_slug, version)

    return package_version_schema.jsonify(version)


@blueprint.route('/packages/<slug:package_slug>/<version:version>', methods=['DELETE'])
def route_delete_version(package_slug, version):
    version = get_version(package_slug, version)

    version.cubby().delete()
    version.delete()

    return success()


@blueprint.route('/packages/<slug:package_slug>/<version:version>', methods=['POST'])
def route_create_version(package_slug, version):
    file = request.files.get('file')

    package = get_package(package_slug)

    existing = package.versions.filter_by(version=version).first()

    if existing is not None:
        raise VersionAlreadyExistsErrorResponse(version, package_slug)

    if file is None or not file.filename.endswith('.zip'):
        detail = f"The package must be provided as a .zip file in the request."
        error = {
            "code": "file-missing",
            "title": "Missing File Argument",
            "detail": detail
        }
        return fail(error, 400)

    try:
        data = json.loads(request.form.get('data'))
        version = existing or PackageVersion(version=version, package=package, **data)
    except Exception as e:
        detail = "'data' must be provided with request files; it must be valid JSON."
        raise InvalidArgumentResponse(code="invalid-argument",
                                      title="'data' file was missing or invalid",
                                      detail=detail)

    if file is not None:
        version.cubby().store(file=file)

    version.save(commit=True)

    return package_version_schema.jsonify(version)
