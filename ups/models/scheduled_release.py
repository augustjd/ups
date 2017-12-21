from ups.database import Model, db, Column, relationship, reference_col, UuidPrimaryKey
from ups.extensions import marshmallow as ma

from .utils import TimezoneAwareDatetime

from .release import Release, release_manifest_schema


class ScheduledRelease(Model, UuidPrimaryKey):
    __bind_key__ = 'packages'
    __tablename__ = "scheduled_releases"

    datetime = Column(TimezoneAwareDatetime, nullable=False)

    release_id = reference_col('releases', nullable=False)
    release = relationship('Release', uselist=False,
                           backref=db.backref('scheduled_releases',
                                              lazy='dynamic'))

    def __repr__(self):
        return self.repr(['datetime', 'release'])


def schedule_release(release, datetime, commit=True):
    if datetime.tzinfo is None:
        raise Exception("datetime passed to schedule_release() must have tzinfo!")
    return ScheduledRelease(release=release, datetime=datetime).save(commit=commit)


def current_release():
    return (Release.query
            .join(ScheduledRelease)
            .filter(ScheduledRelease.datetime.is_past())
            .order_by(ScheduledRelease.datetime.most_recent_first())
            .first())


Release.schedule = schedule_release
Release.current = current_release


class ScheduledReleaseManifestSchema(ma.Schema):
    class Meta:
        fields = ("id", "datetime", "manifest")

    manifest = ma.Nested(release_manifest_schema)


scheduled_release_manifest_schema = ScheduledReleaseManifestSchema()
scheduled_release_manifests_schema = ScheduledReleaseManifestSchema(many=True)
