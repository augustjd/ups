import arrow
import flask
import pytest

from ups.models import (Package, PackageVersion, Release, Suite)


class Factories:
    @pytest.fixture
    def package(self, app):
        package = Package(name='Dog Bog')
        package.save()
        return package

    @pytest.fixture
    def suite(self, package, app):
        suite = Suite(name='Package Suite', packages=[package])
        suite.save()
        return suite

    @pytest.fixture
    def version(self, package, app):
        version = PackageVersion(package=package, version='1.0.0', local='C:/dog-bog')
        version.save()
        return version

    @pytest.fixture
    def version_factory(self, package, app):
        def fn(version='1.0.0'):
            version = PackageVersion(package=package, version=version, local='C:/dog-bog')
            version.save()
            return version

        return fn

    @pytest.fixture
    def suite_release(self, suite, version, app):
        release = Release(suite=suite).save()
        release.set_versions([version], commit=True)
        return release

    @pytest.fixture
    def scheduled_suite_release(self, suite, suite_release, app):
        return suite_release.schedule(arrow.utcnow().shift(minutes=-1), commit=True)

    def _json_cycle(self, o):
        return flask.json.loads(flask.json.dumps(o))

    def assert_json_equal(self, l, r):
        assert self._json_cycle(l) == self._json_cycle(r)
