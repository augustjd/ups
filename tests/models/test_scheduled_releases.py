import pytest

from ups.models import Package, PackageVersion, Namespace, Release

import arrow


class TestScheduledReleases:
    @pytest.fixture
    def namespace(self, app):
        return Namespace(name='Hello').save()

    @pytest.fixture
    def package(self, namespace, app):
        package = Package(name='Dog Bog', namespace=namespace)
        package.save()
        return package

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
    def release(self, version, app):
        release = Release().save()
        release.set_versions([version], commit=True)
        return release

    def test_schedule_release_updates_current(self, release):
        assert Release.current() is None

        scheduled_release = release.schedule(arrow.utcnow().shift(minutes=-1), commit=True)
        assert scheduled_release is not None
        assert scheduled_release.release == release

        assert Release.current() == release

    def test_schedule_release_in_future_does_not_update_current(self, release):
        assert Release.current() is None

        scheduled_release = release.schedule(arrow.utcnow().shift(hours=1),
                                             commit=True)
        assert scheduled_release is not None
        assert scheduled_release.release == release

        current_release = Release.current()
        assert current_release is None  # won't not be None for 1 hr
