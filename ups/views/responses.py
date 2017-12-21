from .errors import (ModelNotFoundErrorResponse,
                     ModelAlreadyExistsErrorResponse,
                     JsonApiErrorResponse)


class PackageNotFoundErrorResponse(ModelNotFoundErrorResponse):
    def __init__(self, namespace_slug, package_slug):
        detail = f"No package with slug '{package_slug}' exists in '{namespace_slug}'."
        return super().__init__(model_name="Package", detail=detail)


class VersionNotFoundErrorResponse(ModelNotFoundErrorResponse):
    def __init__(self, version, package_slug):
        detail = f"No version {version} exists for package '{package_slug}'."
        return super().__init__(model_name="Version", detail=detail)


class NamespaceNotFoundErrorResponse(ModelNotFoundErrorResponse):
    def __init__(self, namespace_slug):
        detail = f"No namespace with slug '{namespace_slug}' exists."
        return super().__init__(model_name="Namespace", detail=detail)


class PackageAlreadyExistsErrorResponse(ModelAlreadyExistsErrorResponse):
    def __init__(self, namespace_slug, package_slug):
        detail = f"A package named '{package_slug}' in namespace '{namespace_slug}' already exists."
        return super().__init__(model_name="Package", detail=detail)


class VersionAlreadyExistsErrorResponse(ModelAlreadyExistsErrorResponse):
    def __init__(self, version, package_slug):
        detail = f"A version {version} already exists for package '{package_slug}' (to update it, use PUT)."
        return super().__init__(model_name="Version", detail=detail)


class NamespaceAlreadyExistsErrorResponse(ModelAlreadyExistsErrorResponse):
    def __init__(self, namespace_slug):
        detail = f"A namespace with slug '{namespace_slug}' already exists."
        return super().__init__(model_name="Namespace", detail=detail)


class ReleaseNotFoundErrorResponse(ModelNotFoundErrorResponse):
    def __init__(self, id):
        detail = f"No release with id '{id}' exists."
        return super().__init__(model_name="Release", detail=detail)


class InvalidArgumentResponse(JsonApiErrorResponse):
    def __init__(self, code=None, title=None, detail=None):
        return super().__init__(code=code,
                                title=title,
                                detail=detail,
                                status=400)