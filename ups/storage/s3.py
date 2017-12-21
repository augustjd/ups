from tempfile import SpooledTemporaryFile

import boto3
from botocore.exceptions import ClientError

from .service import Bucket, Cubby, KeyValueCubby


class S3Bucket(Bucket):
    def __init__(self, name, location, acl='public-read'):
        super().__init__(name, location)

        self.s3 = boto3.resource('s3')
        self.client = boto3.client('s3')

        self._bucket = self.s3.Bucket(name)

        try:
            bucket_configuration = {'LocationConstraint': location}
            self._bucket.create(CreateBucketConfiguration=bucket_configuration)
        except ClientError:
            pass

    def cubby(self, name, content_type=None, acl='public-read'):
        return S3Cubby(self, name, content_type=content_type, acl=acl)

    def service_id(self):
        return "s3"

    def delete(self):
        self._bucket.delete()

    def list(self, prefix=None, max_keys=None, **kwargs):
        if prefix is not None:
            kwargs['prefix'] = prefix
        if max_keys is not None:
            kwargs['max_keys'] = max_keys

        keys = self._bucket.objects.all(**kwargs)

        return [S3Cubby(self, key.name, key=key) for key in keys]


class S3Cubby(KeyValueCubby):
    def __init__(self, bucket, name, content_type=None, acl='public-read', key=None):
        super().__init__(bucket, name)

        self.content_type = content_type

        if key is None:
            self._key = self.bucket._bucket.Object(name)
        else:
            self._key = key
            self.name = self._key.name

        self.acl = acl

    def url(self, duration=Cubby.DefaultUrlDuration):
        return self.bucket.client.generate_presigned_url('get_object',
                                                         Params={
                                                             "Bucket": self.bucket.name,
                                                             "Key": self.key
                                                         },
                                                         ExpiresIn=duration.total_seconds())

    def store_filelike(self, filelike):
        copy = SpooledTemporaryFile()  # boto3 now closes the file.
        copy.write(filelike.read())
        copy.seek(0)

        details = {'ACL': self.acl}

        if self.content_type:
            details['ContentType'] = self.content_type

        self._key.upload_fileobj(copy, ExtraArgs=details)
        return self.url()

    def retrieve_filelike(self, filelike):
        if filelike.closed:
            raise Exception("File provided was already closed.")

        return self._key.download_fileobj(filelike)

    def delete(self):
        return self._key.delete()

    def filesize(self):
        return self._key.content_length

    def service_id(self):
        return "s3"

    def exists(self):
        matches = list(self.bucket._bucket.objects.filter(Prefix=self.key))
        return len(matches) > 0 and matches[0].key == self.key
