from .utils import success
from .responses import (PackageNotFoundErrorResponse,
                        PackageAlreadyExistsErrorResponse,
                        NamespaceNotFoundErrorResponse)
from .blueprint import blueprint

from ups.models import (Package, PackageNamespace, packages_schema, package_schema)


@blueprint.route('/namespaces/<slug:namespace>/', methods=['GET'])
def route_get_all_packages(namespace):
    match = PackageNamespace.get(namespace)

    if match is None:
        raise NamespaceNotFoundErrorResponse(namespace)

    return packages_schema.jsonify(match.packages, many=True)


@blueprint.route('/namespaces/<slug:namespace>/<package>/', methods=['POST'])
def route_create_package(namespace, package):
    match = PackageNamespace.get(namespace)

    if match is None:
        raise NamespaceNotFoundErrorResponse(namespace)

    existing = Package.get(namespace=match, name=package)

    if existing is not None:
        raise PackageAlreadyExistsErrorResponse(namespace, package)

    package = Package(namespace=match, name=package).save()

    return package_schema.jsonify(package, many=True)


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/', methods=['DELETE'])
def route_delete_package(namespace_slug, package_slug):
    match = Package.lookup(namespace_slug, package_slug)

    if match is None:
        raise PackageNotFoundErrorResponse(namespace_slug, package_slug)

    match.delete()

    return success()
