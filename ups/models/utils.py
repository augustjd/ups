import datetime

from flask_login import current_user
from slugify import slugify
from sqlalchemy import event, func
from sqlalchemy_utils import ArrowType, URLType

import sqlalchemy.types as types
from sqlalchemy.types import TypeDecorator

from ups.database import db
from ups.storage import StorageBucket, StorageCubby

from distutils.version import LooseVersion
from pathlib import Path

import pytz


assert(URLType)


PathType = db.Unicode


def SlugMixinFactory(column, **kwargs):
    class SlugMixin:
        slug = db.Column(db.String(), **kwargs)

        @staticmethod
        def compute_slug(target, value, oldvalue, initiator):
            if value and (not target.slug or value != oldvalue):
                target.slug = slugify(value)

        @classmethod
        def __declare_last__(cls):
            event.listen(getattr(cls, column), 'set', cls.compute_slug, retval=False)

    if kwargs.get('primary_key') is True:
        SlugMixin.__primary_key__ = 'slug'

    return SlugMixin


class PathType(types.TypeDecorator):
    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None

        return Path(value)


class VersionType(types.TypeDecorator):
    impl = types.Unicode

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return LooseVersion(value)


def StorageBucketMixinFactory(nullable=False):
    class StorageBucketMixin:
        service = db.Column(db.String, nullable=nullable)        # S3 or Alibaba
        bucket = db.Column(db.String(256), nullable=nullable)    # the bucket
        location = db.Column(db.String(256), nullable=nullable)  # the location (US-West-1 etc.)

        def storage_bucket(self):
            return StorageBucket(f"{self.service}://{self.location}/{self.bucket}")

    return StorageBucketMixin


def StorageCubbyMixinFactory(nullable=False):
    class StorageCubbyMixin:
        service = db.Column(db.String, nullable=nullable)        # S3 or Alibaba
        bucket = db.Column(db.String(256), nullable=nullable)    # the bucket
        location = db.Column(db.String(256), nullable=nullable)  # the location (US-West-1 etc.)
        key = db.Column(db.String(256), nullable=nullable)       # the key
        content_type = db.Column(db.String(256), nullable=True)

        def cubby(self):
            if None in (self.service, self.location, self.bucket, self.key):
                return None

            return StorageCubby(f"{self.service}://{self.location}/{self.bucket}/{self.key}",
                                content_type=self.content_type)

        def set_cubby(self, cubby):
            self.bucket = cubby.bucket.name
            self.key = cubby.name
            self.service = cubby.service
            self.location = cubby.location

    return StorageCubbyMixin


def get_timezone(override=None):
    if override is not None:
        if type(override) == str:
            return pytz.timezone(override)
        else:
            return override
    elif current_user and current_user.is_authenticated and current_user.timezone:
        return current_user.timezone

    return pytz.utc


class TimezoneAwareDatetime(TypeDecorator):
    impl = ArrowType

    class comparator_factory(ArrowType.Comparator):
        def is_past(self):
            return self <= func.now()

        def is_future(self):
            return self > func.now()

        def most_recent_first(self):
            return self.desc()

        def most_recent_last(self):
            return self

        def date(self, tz=None):
            tz = get_timezone(tz)

            if str(db.engine.url).startswith('sqlite'):
                minutes_offset = round(tz.utcoffset(datetime.datetime.now()).total_seconds() / 60)
                return func.date(self.expr, f'{minutes_offset} minutes')
            else:
                tzname = tz.tzname(datetime.datetime.now())
                datetime_at_tz = func.timezone(tzname, self.expr)
                return func.DATE(datetime_at_tz)
