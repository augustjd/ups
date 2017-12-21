import datetime
import io
import os


class Bucket:
    def __init__(self, name, location):
        self.name = name
        self.location = location

    def cubby(self, name):
        raise NotImplementedError()

    def service_id(self):
        raise NotImplementedError()

    def __str__(self):
        return "{}://{}/{}".format(self.service_id(), self.location, self.name)

    def delete(self):
        raise NotImplementedError()

    def list(self, prefix=None, max_keys=None):
        raise NotImplementedError()


class Cubby:
    def retrieve(self, filepath=None, file=None, bytes=None):
        if filepath is not None:
            if os.path.isdir(filepath):
                filepath = os.path.join(filepath, self.name)

            return self.retrieve_filepath(filepath)
        elif file is not None:
            return self.retrieve_filelike(file)
        elif bytes is not None:
            return self.retrieve_filelike(bytes)
        else:
            buffer = io.BytesIO()
            self.retrieve_filelike(buffer)
            buffer.seek(0)
            return buffer.read()

    def retrieve_filepath(self, filepath):
        with open(filepath, 'wb') as file:
            return self.retrieve_filelike(file)

    def retrieve_filelike(self, file):
        raise NotImplementedError()

    def store(self, filepath=None, file=None, string=None, bytes=None):
        if filepath is not None:
            self.store_filepath(filepath)
        elif file is not None:
            self.store_filelike(file)
        elif string is not None:
            self.store_filelike(io.BytesIO(string.encode("utf-8")))
        elif bytes is not None:
            self.store_filelike(io.BytesIO(bytes))
        else:
            raise Exception("One of [filepath, file, string, bytes] must be specified.")

        return self

    def store_filepath(self, filepath):
        with open(filepath, 'rb') as file:
            return self.store_filelike(file)

    def store_filelike(self, filelike):
        raise NotImplementedError()

    DefaultUrlDuration = datetime.timedelta(weeks=52 * 3)  # 3 years

    def url(self, duration=DefaultUrlDuration):
        raise NotImplementedError()

    def filesize(self):
        return NotImplementedError()

    @property
    def extension(self):
        return os.path.splitext(self.key)[1]

    def delete(self):
        return NotImplementedError()

    def exists(self):
        return NotImplementedError()

    def service_id(self):
        return self.bucket.service_id()

    def contents(self):
        result = io.BytesIO()
        self.retrieve(bytes=result)
        result.seek(0)
        return result.read()


class KeyValueCubby(Cubby):
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def __str__(self):
        return "{}/{}".format(self.bucket, self.key)
