from .utils import success, fail
from .blueprint import blueprint
from .responses import (VersionNotFoundErrorResponse, VersionAlreadyExistsErrorResponse)

from flask import request

from ups.models import (PackageVersion, package_version_schema,
                        package_with_versions_schema)

from .package_views import get_package


def get_version(namespace_slug, package_slug, version):
    package = get_package(namespace_slug, package_slug)

    version = package.versions.filter_by(version=version).first()

    if version is None:
        raise VersionNotFoundErrorResponse(version, package_slug)

    return version


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/', methods=['GET'])
def route_get_package(namespace_slug, package_slug):
    match = get_package(namespace_slug, package_slug)
    print(match.versions.all())
    return package_with_versions_schema.jsonify(match)


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/<version:version>',
                 methods=['GET'])
def route_get_version(namespace_slug, package_slug, version):
    version = get_version(namespace_slug, package_slug, version)

    return package_version_schema.jsonify(version)


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/<version:version>',
                 methods=['DELETE'])
def route_delete_version(namespace_slug, package_slug, version):
    version = get_version(namespace_slug, package_slug, version)

    version.cubby().delete()
    version.delete()

    return success()


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/<version:version>',
                 methods=['POST', 'PUT'])
def route_create_version(namespace_slug, package_slug, version):
    file = request.files.get('file')

    package = get_package(namespace_slug, package_slug)

    existing = package.versions.filter_by(version=version).first()

    if request.method == 'POST':
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

    data = request.get_json() or {}

    if 'version' in data:
        error = {
            "code": "invalid-argument",
            "title": "Version Cannot Change",
            "detail": "Package versions may not change their version strings."
        }
        return fail(error, 400)

    version = existing or PackageVersion(version=version, package=package, **data)

    if file is not None:
        version.cubby().store(file=file)

    version.update(**data)

    return package_version_schema.jsonify(version)
