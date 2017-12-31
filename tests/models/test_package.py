import pytest

import sqlalchemy

from ups.models import Package, PackageVersion, Version

from pathlib import PosixPath


class TestPackages:
    def test_packages_get_slug(self, app):
        p = Package(name='Dog Bog')
        assert p.slug == 'dog-bog'  # slug is set BEFORE commit
        p.save()
        assert p.slug == 'dog-bog'  # slug is set AFTER commit

    def test_package_version_local_is_pathtype(self, app):
        p = Package(name='Dog Bog')
        v = PackageVersion(package=p, version='1.0.0',
                           local='C:/dog-bog')

        assert type(v.local) is str
        v.save()
        assert type(v.local) is PosixPath

    def test_package_versions_are_versiontype(self, app):
        p = Package(name='Dog Bog')

        assert p.versions.all() == []

        v = PackageVersion(package=p, version='1.0.0',
                           local='C:/dog-bog')
        assert type(v.version) is str
        v.save()
        assert type(v.version) is Version

    def test_package_versions_are_unique(self, app):
        p = Package(name='Dog Bog')

        assert p.versions.all() == []

        v1 = PackageVersion(package=p, version='1.0.0',
                            local='C:/dog-bog')
        v1.save()

        assert p.versions.all() == [v1]

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            v2 = PackageVersion(package=p, version='1.0.0',
                                local='C:/dog-bog')
            v2.save()

        app.db.session.rollback()

        assert p.versions.all() == [v1]

    def test_package_duplicates_not_allowed(self, app):
        p = Package(name='Dog Bog')
        p.save()

        p2 = Package(name='Dog Bog')

        with pytest.raises(sqlalchemy.exc.SQLAlchemyError):
            p2.save()

        app.db.session.rollback()
