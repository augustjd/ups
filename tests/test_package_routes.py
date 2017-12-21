from ups.models import Package, PackageVersion, PackageNamespace


class TestPackageRoutes:
    def test_get_all_packages(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        response = client.get(f"/api/v1/namespaces/{n.slug}/")
        assert response.status_code == 200
        assert response.json[0] == {"name": p.name}

    def test_get_all_packages_returns_404(self, app, client):
        response = client.get(f"/api/v1/namespaces/not-a-namespace/")
        assert response.status_code == 404
        assert response.json['errors'][0]['status'] == 404
        assert response.json['errors'][0]['title'] == "Namespace Not Found"

    def test_create_namespace(self, app, client):
        name = "Dog Gone Shame"
        response = client.post(f"/api/v1/namespaces/{name}/")
        assert response.status_code == 200

        match = PackageNamespace.get(name=name)
        assert match is not None
        assert match.slug == 'dog-gone-shame'

    def test_delete_namespace(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        v = PackageVersion(package=p, version='1.0.0', local='C:/dog-bog')
        v.save()

        assert PackageNamespace.query.count() == 1
        response = client.delete(f"/api/v1/namespaces/{n.slug}/")
        assert response.status_code == 200
        assert PackageNamespace.query.count() == 0
