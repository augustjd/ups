from ups.models import Package, PackageVersion


class TestPackageRoutes:
    def test_get_one_package(self, app, client):
        p = Package(name='Dog Bog')
        p.save()

        response = client.get(f"/api/v1/packages/{p.slug}")

        assert response.status_code == 200
        assert response.json == {"name": p.name, "slug": p.slug, "versions": []}

    def test_get_nonexistant_package_returns_404(self, app, client):
        response = client.get(f"/api/v1/packages/not-a-package")

        assert response.status_code == 404
        assert response.json['errors'][0]['status'] == 404
        assert response.json['errors'][0]['title'] == "Package Not Found"

    def test_create_package(self, app, client):
        name = "Dog Gone Shame"

        response = client.post(f"/api/v1/packages/{name}")
        assert response.status_code == 200

        match = Package.get(name=name)
        assert match is not None
        assert match.slug == 'dog-gone-shame'

    def test_delete_package(self, app, client):
        p = Package(name='Dog Bog')
        p.save()

        v = PackageVersion(package=p, version='1.0.0', local='C:/dog-bog')
        v.save()

        assert Package.query.count() == 1
        response = client.delete(f"/api/v1/packages/{p.slug}")
        assert response.status_code == 200
        assert Package.query.count() == 0
