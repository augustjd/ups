from moto import mock_s3

from io import BytesIO

from ups.models import Package, PackageVersion, PackageNamespace

from pathlib import PosixPath


class TestVersionRoutes:
    @mock_s3
    def test_get_all_versions(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        response = client.get(f"/api/v1/namespaces/{n.slug}/{p.slug}/")
        assert response.status_code == 200
        assert response.json == []

        v = PackageVersion(package=p, version='1.0.0',
                           local='C:/dog-bog')
        v.save()

        response = client.get(f"/api/v1/namespaces/{n.slug}/{p.slug}/")
        assert response.status_code == 200
        assert response.json[0]['local'] == str(v.local)
        assert response.json[0]['version'] == str(v.version)

    def test_get_single_package_when_package_does_not_exist_returns_404(self, app, client):
        response = client.get(f"/api/v1/namespaces/not-a-namespace/not-a-package/")
        assert response.status_code == 404
        print(response.json)
        assert response.json['errors'][0]['status'] == 404
        assert response.json['errors'][0]['title'] == "Package Not Found"

    def test_get_single_version_when_package_does_not_exist_returns_404(self, app, client):
        response = client.get(f"/api/v1/namespaces/not-a-namespace/not-a-package/1.0.03")
        assert response.status_code == 404
        assert response.json['errors'][0]['status'] == 404
        assert response.json['errors'][0]['title'] == "Package Not Found"

    def test_get_single_version_when_version_does_not_exist_returns_404(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package(name='Dog Bog', namespace=n)
        p.save()

        response = client.get(f"/api/v1/namespaces/{n.slug}/{p.slug}/1.0.03")
        assert response.status_code == 404
        assert response.json['errors'][0]['status'] == 404
        assert response.json['errors'][0]['title'] == "Version Not Found"

    @mock_s3
    def test_get_single_version_200(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)
        v = PackageVersion.create(package=p, version='1.0.0',
                                  local='C:/dog-bog')

        response = client.get(f"/api/v1/namespaces/{n.slug}/{p.slug}/{v.version}")
        assert response.status_code == 200

        assert response.json['local'] == str(v.local)
        assert response.json['version'] == str(v.version)

    @mock_s3
    def test_post_single_version_200(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        bytes = b'not a zip!'
        response = client.post(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                               data={"file": (BytesIO(bytes), "workstation.zip")})

        assert response.status_code == 200
        assert response.json['remote'] is not None
        assert response.json["local"] is None

        version = PackageVersion.query.one()
        assert version.cubby().contents() == bytes

    @mock_s3
    def test_post_twice_fails(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        response = client.post(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                               data={"file": (BytesIO(b"not a zip!"), "workstation.zip")})
        assert response.status_code == 200

        response = client.post(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                               data={"file": (BytesIO(b"not a zip!"), "workstation.zip")})
        assert response.status_code == 400
        assert response.json['errors'][0]['title'] == 'Version Already Exists'

    @mock_s3
    def test_put_twice_updates_package_file(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        bytes1 = b'not a zip'
        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              data={"file": (BytesIO(bytes1), "workstation.zip")})
        assert response.status_code == 200

        bytes2 = b'something different'
        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              data={"file": (BytesIO(bytes2), "workstation.zip")})
        assert response.status_code == 200

        assert PackageVersion.query.one().cubby().contents() == bytes2

    @mock_s3
    def test_put_updates_package_version_data(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        bytes1 = b'not a zip'
        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              data={"file": (BytesIO(bytes1), "workstation.zip")})
        assert response.status_code == 200

        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              json={"local": "C:/bobo/"})
        assert response.status_code == 200

        version = PackageVersion.query.one()
        assert version.local == PosixPath("C:/bobo/")

    @mock_s3
    def test_put_cannot_update_package_version_version(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        bytes1 = b'not a zip'
        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              data={"file": (BytesIO(bytes1), "workstation.zip")})
        assert response.status_code == 200

        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              json={"version": "C:/bobo/"})
        assert response.status_code == 400

    @mock_s3
    def test_delete_single_version_200_with_no_s3_file(self, app, client):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)
        v = PackageVersion.create(package=p, version='1.0.0',
                                  local='C:/dog-bog')

        response = client.delete(f"/api/v1/namespaces/{n.slug}/{p.slug}/{v.version}")
        assert response.status_code == 200

        assert PackageVersion.query.count() == 0

    @mock_s3
    def test_delete_single_version_200_deletes_s3_file(self, app, client, test_media_directory):
        n = PackageNamespace(name='Hello')
        p = Package.create(name='Dog Bog', namespace=n)

        version = '1.0.0'

        bytes1 = b'not a zip'
        response = client.put(f"/api/v1/namespaces/{n.slug}/{p.slug}/{version}",
                              data={"file": (BytesIO(bytes1), "workstation.zip")})

        assert response.status_code == 200

        v = PackageVersion.query.first()

        assert v.cubby().exists() is True

        response = client.delete(f"/api/v1/namespaces/{n.slug}/{p.slug}/{v.version}")
        assert response.status_code == 200

        assert PackageVersion.query.count() == 0

        assert v.cubby().exists() is False
