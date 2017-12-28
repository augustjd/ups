import flask

from ups.models import (Package, Namespace, Suite, packages_schema,
                        package_versions_schema)

from slugify import slugify

from moto import mock_s3

from tests.factories import Factories


class TestSuiteRoutes(Factories):
    def test_get_single_suite(self, app, client):
        n = Namespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        s = Suite(name="Suite", packages=[p])
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
        s = Suite(name="Suite", packages=[])
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
        s = Suite(name="Suite", packages=[p])
        s.save()

        response = client.delete(f"/api/v1/suites/{s.slug}/")
        assert response.status_code == 200

        assert Suite.query.count() == 0

    def test_update_suite_packages_packages_must_exist(self, app, client):
        s = Suite(name="Suite", packages=[])
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
        s = Suite(name="Suite", packages=[p])
        s.save()

        assert s.packages == [p]

        response = client.put(f"/api/v1/suites/{s.slug}/packages", json=[])

        assert response.status_code == 200
        assert s.packages == []

    def test_get_suite_current_version_starts_404(self, app, client, suite):
        response = client.get(f"/api/v1/suites/{suite.slug}/current")

        assert response.status_code == 404

    @mock_s3
    def test_get_suite_with_version_returns_manifest_200(self, app, client,
                                                         suite, scheduled_suite_release):
        response = client.get(f"/api/v1/suites/{suite.slug}/current")

        assert suite.current_release() is not None
        assert response.status_code == 200
        assert len(response.json['packages']) == len(suite.packages)

        expected = package_versions_schema.dump(suite.current_release().package_versions).data
        self.assert_json_equal(response.json['packages'], expected)
