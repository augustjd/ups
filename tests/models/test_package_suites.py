import pytest

import sqlalchemy.exc

from ups.models import Package, PackageNamespace, PackageSuite


class TestPackageSuites:
    def test_suites_have_packages(self, app):
        n1 = PackageNamespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n1)

        n2 = PackageNamespace(name='Bello')
        p2 = Package(name='Trog Mog', namespace=n2)
        s = PackageSuite(name='Everything', packages=[p1, p2])
        s.save()

        assert s.packages == [p1, p2]

    def test_suites_have_packages_once(self, app):
        """A package can either belong to a suite or not; it cannot belong twice."""
        n1 = PackageNamespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n1)

        with pytest.raises(sqlalchemy.exc.IntegrityError):
            s = PackageSuite(name='Everything', packages=[p1, p1])
            s.save()

    def test_packages_have_suites(self, app):
        """Packages belong to suites through a backref."""
        n1 = PackageNamespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n1)

        n2 = PackageNamespace(name='Bello')
        p2 = Package(name='Trog Mog', namespace=n2)
        s = PackageSuite(name='Everything', packages=[p1, p2])
        s.save()

        assert p1.suites == [s]
        assert p2.suites == [s]

    def test_append_package_after_creation(self, app):
        n1 = PackageNamespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n1)

        n2 = PackageNamespace(name='Bello')
        p2 = Package(name='Trog Mog', namespace=n2)
        s = PackageSuite(name='Everything', packages=[p1])
        s.save()

        assert s.packages == [p1]

        s.packages.append(p2)
        s.save()

        assert s.packages == [p1, p2]

    def test_query_packages_belonging_to_suite(self, app):
        n1 = PackageNamespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n1)

        n2 = PackageNamespace(name='Bello')
        p2 = Package(name='Trog Mog', namespace=n2)
        s = PackageSuite(name='Everything', packages=[p1, p2])
        s.save()

        packages = Package.query.filter(Package.suites.contains(s)).all()
        assert packages == [p1, p2]
