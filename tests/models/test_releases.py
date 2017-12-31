import pytest

import sqlalchemy.exc

from ups.models import Package, PackageVersion, Release
from ups.models.release import ReleasePackage, release_manifest_schema

from moto import mock_s3


class TestPackages:
    @pytest.fixture
    def package(self):
        package = Package(name='Dog Bog')
        package.save()
        return package

    @pytest.fixture
    def version(self, package):
        version = PackageVersion(package=package, version='1.0.0', local='C:/dog-bog')
        version.save()
        return version

    @pytest.fixture
    def version_factory(self, package):
        def fn(version='1.0.0'):
            version = PackageVersion(package=package, version=version, local='C:/dog-bog')
            version.save()
            return version

        return fn

    def test_release_has_versions(self, app, version):
        release = Release().save()

        assert len(release.package_versions) == 0

        release.set_versions([version], commit=True)

        assert version.releases == [release]

        assert release.packages == [version.package]
        assert release.package_versions == [version]

    def test_cannot_set_two_versions_of_same_package(self, app, version, version_factory):
        release = Release().save()

        assert len(release.package_versions) == 0

        v2 = version_factory('2.0.0')

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            release.set_versions([version, v2])
            release.save()

    @mock_s3
    def test_release_serialize_manifest(self, app, version):
        release = Release().save()
        release.set_versions([version], commit=True)

        data = release_manifest_schema.dump(release).data  # actually generates
                                                           # version.url; so don't do this after
                                                           # expected

        expected = {
            "title": None,
            "packages": [{"remote": version.url,
                          "local": version.local,
                          "version": version.version,
                          "name": version.package.name,
                          "run": version.run,
                          "test": version.test}]
        }

        print(data)
        print(expected)

        assert data == expected
