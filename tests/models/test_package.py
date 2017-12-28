import pytest

import sqlalchemy

from ups.models import Package, PackageVersion, Namespace

from pathlib import PosixPath
from distutils.version import LooseVersion


class TestPackages:
    def test_packages_get_slug(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        assert p.slug == 'dog-bog'  # slug is set BEFORE commit
        p.save()
        assert p.slug == 'dog-bog'  # slug is set AFTER commit

    def test_package_version_local_is_pathtype(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)
        v = PackageVersion(package=p, version='1.0.0',
                           local='C:/dog-bog')

        assert type(v.local) is str
        v.save()
        assert type(v.local) is PosixPath

    def test_package_versions_are_versiontype(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)

        assert p.versions.all() == []

        v = PackageVersion(package=p, version='1.0.0',
                           local='C:/dog-bog')
        assert type(v.version) is str
        v.save()
        assert type(v.version) is LooseVersion

    def test_package_versions_are_unique(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)

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

    def test_package_lookup(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)

        p.save()

        assert Package.lookup("Hello", "dog bog") == p
        assert Package.lookup("Hello sop", "dog bog") is None
        assert Package.lookup("Hello", "dog nope") is None

    def test_package_duplicates_allowed_in_seperate_namespaces(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)

        p.save()

        n2 = Namespace(name='Yellow')
        p2 = Package(name='Dog Bog',
                     namespace=n2)

        p2.save()

    def test_package_duplicates_not_allowed_in_same_namespace(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog',
                    namespace=n)

        p.save()

        p2 = Package(name='Dog Bog',
                     namespace=n)

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            p2.save()

        app.db.session.rollback()

    def test_namespace_list_packages(self, app):
        n = Namespace(name='Hello').save()
        assert n.packages.all() == []

        p = Package(name='Dog Bog', namespace=n)
        p.save()

        assert n.packages.all() == [p]

    def test_package_path(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)

        expected_path = 'hello/dog-bog'

        assert p.path == expected_path
        p.save()
        assert p.path == expected_path

    def test_lookup_path(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        expected_path = 'hello/dog-bog'

        assert Package.lookup_path(expected_path) == p

    def test_lookup_paths(self, app):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        n2 = Namespace(name='Molten')
        n2.save()
        p2 = Package(name='Dog Bog', namespace=n2)
        p2.save()

        expected_path = 'hello/dog-bog'

        assert Package.lookup_paths([expected_path]) == [p]
