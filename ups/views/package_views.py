from .utils import fail, success
from .responses import (PackageNotFoundErrorResponse,
                        NamespaceNotFoundErrorResponse,
                        NamespaceAlreadyExistsErrorResponse,
                        PackageAlreadyExistsErrorResponse)
from .blueprint import blueprint

from ups.models import (Package, PackageNamespace, packages_schema,
                        package_schema, package_namespace_schema)

from slugify import slugify


@blueprint.route('/namespaces/<slug:namespace>/', methods=['GET'])
def route_get_all_packages(namespace):
    match = PackageNamespace.get(namespace)

    if match is None:
        return NamespaceNotFoundErrorResponse(namespace)

    return packages_schema.jsonify(match.packages, many=True)


@blueprint.route('/namespaces/<slug:namespace>/', methods=['DELETE'])
def route_delete_namespace(namespace):
    match = PackageNamespace.get(namespace)

    if match is None:
        return NamespaceNotFoundErrorResponse(namespace)

    match.delete(commit=True)

    return success()


@blueprint.route('/namespaces/<namespace>/', methods=['POST'])
def route_create_namespace(namespace):
    namespace_slug = slugify(namespace)
    existing = PackageNamespace.get(namespace_slug)

    if existing is not None:
        return NamespaceAlreadyExistsErrorResponse(namespace)

    namespace = PackageNamespace(name=namespace).save()

    return package_namespace_schema.jsonify(namespace)


@blueprint.route('/namespaces/<slug:namespace>/<package>/', methods=['POST'])
def route_create_package(namespace, package):
    match = PackageNamespace.get(namespace)

    if match is None:
        return NamespaceNotFoundErrorResponse(namespace)

    existing = Package.get(namespace=match, name=package)

    if existing is not None:
        return PackageAlreadyExistsErrorResponse(namespace, package)

    package = Package(namespace=match, name=package).save()

    return package_schema.jsonify(package, many=True)


@blueprint.route('/namespaces/<slug:namespace_slug>/<slug:package_slug>/', methods=['DELETE'])
def route_delete_package(namespace_slug, package_slug):
    match = Package.lookup(namespace_slug, package_slug)

    if match is None:
        return PackageNotFoundErrorResponse(namespace_slug, package_slug)

    match.delete()

    return success()
