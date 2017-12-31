from flask import request

from .blueprint import blueprint
from .errors import (ErrorResponse)
from .responses import (PackageNotFoundErrorResponse,
                        SuiteNotFoundErrorResponse,
                        SuiteAlreadyExistsErrorResponse,
                        SuiteReleaseNotFoundErrorResponse)
from .utils import success, validate_request_json

from ups.models import (Package, Suite, suite_schema,
                        release_manifest_schema)

from slugify import slugify


def get_suite(suite_slug):
    match = Suite.get(suite_slug)

    if match is None:
        raise SuiteNotFoundErrorResponse(suite_slug)

    return match


@blueprint.route('/suites/<slug:suite>/', methods=['GET'])
def route_get_suite(suite):
    match = get_suite(suite)

    return suite_schema.jsonify(match)


@blueprint.route('/suites/<slug:suite>/current', methods=['GET'])
def route_get_current_suite_manifest(suite):
    suite = get_suite(suite)

    release = suite.current_release()

    if release is None:
        raise SuiteReleaseNotFoundErrorResponse(suite)

    return release_manifest_schema.jsonify(release)


@blueprint.route('/suites/<slug:suite>/', methods=['DELETE'])
def route_delete_suite(suite):
    match = get_suite(suite)

    match.delete(commit=True)

    return success()


@blueprint.route('/suites/<suite>/', methods=['POST'])
def route_create_suite(suite):
    suite_slug = slugify(suite)
    existing = Suite.get(suite_slug)

    if existing is not None:
        raise SuiteAlreadyExistsErrorResponse(suite)

    suite = Suite(name=suite).save()

    return suite_schema.jsonify(suite)


@blueprint.route('/suites/<slug:suite_slug>/packages', methods=['PUT'])
@validate_request_json("schemas/suite_packages.json")
def route_update_suite_packages(suite_slug):
    suite = get_suite(suite_slug)

    slugs = request.json

    packages = Package.lookup_slugs(slugs)

    package_slugs = [p.slug for p in packages]
    missing_slugs = [slug for slug in slugs if slug not in package_slugs]

    if missing_slugs:
        raise ErrorResponse(errors=[PackageNotFoundErrorResponse(slug) for slug in missing_slugs],
                            status=400)

    suite.packages = packages
    suite.save()

    return suite_schema.jsonify(suite)
