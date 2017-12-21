import pytest

import os
import json

from ups import create_app

from flask.testing import FlaskClient


class TestClient(FlaskClient):
    def open(self, *args, **kwargs):
        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            kwargs['content_type'] = 'application/json'

        return super(TestClient, self).open(*args, **kwargs)


@pytest.yield_fixture(scope='function')
def app():
    app = create_app('test')
    app.test_client_class = TestClient

    return app


@pytest.fixture
def test_media_directory():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'media')
