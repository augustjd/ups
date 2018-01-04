from .utils import success
from .responses import (PackageNotFoundErrorResponse,
                        PackageAlreadyExistsErrorResponse)
from .blueprint import blueprint

from ups.models import (Package, package_schema,
                        package_with_versions_schema,
                        packages_with_versions_schema)

from slugify import slugify


def get_package(name):
    match = Package.get(slugify(name))

    if match is None:
        raise PackageNotFoundErrorResponse(name)

    return match


@blueprint.route('/packages/<name>', methods=['POST'])
def route_create_package(name):
    slug = slugify(name)
    existing = Package.get(slug)

    if existing is not None:
        raise PackageAlreadyExistsErrorResponse(name)

    package = Package(name=name, slug=slug).save()

    return package_schema.jsonify(package)


@blueprint.route('/packages/', methods=['GET'])
def route_list_packages():
    return packages_with_versions_schema.jsonify(Package.all(), many=True)


@blueprint.route('/packages/<name>', methods=['GET'])
def route_get_package(name):
    match = get_package(name)
    return package_with_versions_schema.jsonify(match)


@blueprint.route('/packages/<name>', methods=['DELETE'])
def route_delete_package(name):
    match = get_package(name)

    match.delete()

    return success()
