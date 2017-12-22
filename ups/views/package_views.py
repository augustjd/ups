from .utils import success
from .responses import (PackageNotFoundErrorResponse,
                        PackageAlreadyExistsErrorResponse,
                        NamespaceNotFoundErrorResponse)
from .blueprint import blueprint

from ups.models import (Package, PackageNamespace, packages_schema, package_schema)

from slugify import slugify


def get_namespace(namespace_slug):
    match = PackageNamespace.get(namespace_slug)

    if match is None:
        raise NamespaceNotFoundErrorResponse(namespace_slug)

    return match


def get_package(namespace_slug, package_slug):
    path = f'{namespace_slug}/{package_slug}'
    match = Package.lookup_path(path)

    if match is None:
        raise PackageNotFoundErrorResponse(path)

    return match


@blueprint.route('/namespaces/<slug:namespace>/', methods=['GET'])
def route_get_all_packages(namespace):
    match = get_namespace(namespace)

    return packages_schema.jsonify(match.packages, many=True)


@blueprint.route('/namespaces/<slug:namespace>/<package>/', methods=['POST'])
def route_create_package(namespace, package):
    match = get_namespace(namespace)

    existing = Package.get(namespace=match, name=package)

    if existing is not None:
        package_slug = slugify(package)
        raise PackageAlreadyExistsErrorResponse(f'{namespace}/{package_slug}')

    package = Package(namespace=match, name=package).save()

    return package_schema.jsonify(package, many=True)


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/', methods=['DELETE'])
def route_delete_package(namespace_slug, package_slug):
    match = get_package(namespace_slug, package_slug)

    match.delete()

    return success()
