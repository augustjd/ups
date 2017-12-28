from ups.models import Package, PackageVersion, Namespace, PackageSuite, packages_schema

from slugify import slugify


class TestPackageSuiteRoutes:
    def test_get_single_suite(self, app, client):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        s = PackageSuite(name="Suite", packages=[p])
        s.save()

        response = client.get(f"/api/v1/suites/{s.slug}/")
        assert response.status_code == 200
        assert response.json['packages'] == packages_schema.dump([p]).data
        assert response.json['slug'] == s.slug

    def test_create_suite(self, app, client):
        suite_name = "Heavenly Suite"
        response = client.post(f"/api/v1/suites/{suite_name}/")
        assert response.status_code == 200
        assert response.json['slug'] == slugify(suite_name)
        assert response.json['name'] == suite_name

    def test_update_suite_packages(self, app, client):
        s = PackageSuite(name="Suite", packages=[])
        s.save()

        n = Namespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n)
        p2 = Package(name='Mog', namespace=n)
        app.db.session.add(p1)
        app.db.session.add(p2)
        app.db.session.add(n)
        app.db.session.commit()

        response = client.put(f"/api/v1/suites/{s.slug}/packages", json=["hello/dog-bog", "hello/mog"])

        assert response.status_code == 200
        assert response.json['packages'] == packages_schema.dump([p1, p2]).data

        assert p1.suites == [s]
        assert p2.suites == [s]
        assert set(s.packages) == set([p1, p2])

    def test_delete_suite(self, app, client):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        s = PackageSuite(name="Suite", packages=[p])
        s.save()

        response = client.delete(f"/api/v1/suites/{s.slug}/")
        assert response.status_code == 200

        assert PackageSuite.query.count() == 0

    def test_update_suite_packages_packages_must_exist(self, app, client):
        s = PackageSuite(name="Suite", packages=[])
        s.save()

        n = Namespace(name='Hello')
        p1 = Package(name='Dog Bog', namespace=n)
        p1.save()

        response = client.put(f"/api/v1/suites/{s.slug}/packages", json=["hello/dog-bog", "hello/mog"])

        assert response.status_code == 400
        assert s.packages == []

        response = client.put(f"/api/v1/suites/{s.slug}/packages", json=["hello/dog-bog"])

        assert response.status_code == 200
        assert s.packages == [p1]

    def test_update_suite_remove_packages(self, app, client):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        s = PackageSuite(name="Suite", packages=[p])
        s.save()

        assert s.packages == [p]

        response = client.put(f"/api/v1/suites/{s.slug}/packages", json=[])

        assert response.status_code == 200
        assert s.packages == []
