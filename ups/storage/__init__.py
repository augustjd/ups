from .s3 import S3Bucket

from flask import current_app
from ups.log import log

import re
import boto3


STORAGE_BUCKET_REGEX = \
    re.compile(r"(?P<service>(s3)):\/\/(?P<location>[^\/]+)\/(?P<bucket>[^\/]+)")
STORAGE_STRING_REGEX = \
    re.compile(r"{}\/(?P<key>.+)".format(STORAGE_BUCKET_REGEX.pattern))


def StorageBucket(string):
    match = STORAGE_BUCKET_REGEX.match(string)

    if match is None:
        raise Exception('Invalid storage string "{}"!'.format(string))

    d = match.groupdict()

    if d['service'] == 's3' or current_app.config['TESTING']:
        return S3Bucket(name=d['bucket'], location=d['location'])
    else:
        raise Exception('Invalid storage service "{service}" requested.'.format(**d))


def StorageCubby(string, content_type=None):
    bucket = StorageBucket(string)
    match = STORAGE_STRING_REGEX.match(string)
    return bucket.cubby(match.groupdict()['key'], content_type=content_type)


class Storage(object):
    def __init__(self, app=None):
        self.default_service = None
        self.default_location = None
        self.default_bucket = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.config.setdefault('STORAGE_DEFAULT_SERVICE', 's3')
        app.config.setdefault('STORAGE_DEFAULT_LOCATION', 'us-west-1')

        self.default_service = self.app.config['STORAGE_DEFAULT_SERVICE']
        self.default_location = self.app.config['STORAGE_DEFAULT_LOCATION']
        self.default_bucket = self.app.config.get('STORAGE_DEFAULT_BUCKET')

        aws_access_key_id = app.config.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = app.config.get('AWS_SECRET_ACCESS_KEY')

        if aws_access_key_id is None and not app.debug:
            log.error("'AWS_ACCESS_KEY_ID' is not set.")

        if aws_secret_access_key is None and not app.debug:
            log.error("'AWS_SECRET_ACCESS_KEY' is not set.")

        self.session = boto3.Session(region_name=app.config['STORAGE_DEFAULT_LOCATION'],
                                     aws_access_key_id=aws_access_key_id,
                                     aws_secret_access_key=aws_secret_access_key)

    @property
    def bucket(self):
        if self.app is None:
            raise RuntimeError("Storage.init_app() was not called!")

        if self.default_bucket is None:
            raise Exception("'STORAGE_DEFAULT_BUCKET' is not set!")

        return StorageBucket(f"{default_service}://{default_location}/{default_bucket}/")

    def store(self, request_file):
        cubby = self.default_bucket.cubby(request_file.name)
        return cubby.store(file=request_file)
