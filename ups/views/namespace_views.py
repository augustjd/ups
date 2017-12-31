from .blueprint import blueprint
from .responses import (NamespaceNotFoundErrorResponse,
                        NamespaceAlreadyExistsErrorResponse)
from .utils import success

from ups.models import (Namespace, namespace_schema, namespaces_schema)

from slugify import slugify


@blueprint.route('/namespaces/<slug:namespace>/', methods=['DELETE'])
def route_delete_namespace(namespace):
    match = Namespace.get(namespace)

    if match is None:
        raise NamespaceNotFoundErrorResponse(namespace)

    match.delete(commit=True)

    return success()


@blueprint.route('/namespaces/<namespace>/', methods=['POST'])
def route_create_namespace(namespace):
    namespace_slug = slugify(namespace)
    existing = Namespace.get(namespace_slug)

    if existing is not None:
        raise NamespaceAlreadyExistsErrorResponse(namespace)

    namespace = Namespace(name=namespace).save()

    return namespace_schema.jsonify(namespace)


@blueprint.route('/namespaces/', methods=['GET'])
def route_get_all_namespaces():
    existing = Namespace.all()

    return namespaces_schema.jsonify(existing)
