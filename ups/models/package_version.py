from flask import current_app
from ups.database import Model, db, Column, reference_col, relationship, UuidPrimaryKey

from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import validates

from .utils import (URLType, PathType, VersionType, StorageCubbyMixinFactory)
from ups.extensions import marshmallow as ma

from .package import Package


class PackageVersion(Model, UuidPrimaryKey, StorageCubbyMixinFactory(nullable=False)):
    __bind_key__ = 'packages'
    __tablename__ = "package_versions"

    version = Column(VersionType, nullable=False)

    local = Column(PathType, nullable=True)
    run = Column(db.String, nullable=True)
    test = Column(db.String, nullable=True)
    url = Column(URLType, nullable=True)

    package_id = reference_col("packages", nullable=False)
    package = relationship(Package, backref=db.backref('versions',
                                                       cascade='delete',
                                                       lazy='dynamic'))

    @validates('version')
    def version_readonly(self, key, value):
        existing = getattr(self, key)

        if existing is not None:
            raise ValueError("'version' can only be written once.")

        return value

    def __init__(self, *args, cubby=None, **kwargs):
        if cubby is not None:
            self.set_cubby(cubby)
        else:
            kwargs['service'] = current_app.storage.default_service
            kwargs['location'] = current_app.storage.default_location
            kwargs['bucket'] = current_app.storage.default_bucket
            package = kwargs.get('package') or Package.get(kwargs.get('package_id'))
            version = kwargs.get('version')
            kwargs['key'] = f'{package.slug}/{package.slug}-{version}.zip'
            kwargs['content_type'] = 'application/zip'

        Model.__init__(self, *args, **kwargs)

    @property
    def remote(self):
        if not self.url and self.cubby():
            self.update(url=self.cubby().url(), commit=True)

        return self.url

    __table_args__ = (
        UniqueConstraint('package_id', 'version', name='package_version_tuple_is_unique'),
    )


class PackageVersionSchema(ma.Schema):
    class Meta:
        fields = ("remote", "local", "version", "name", "run", "test")

    name = ma.Function(lambda version: version.package.name if version.package else None)


package_version_schema = PackageVersionSchema()
package_versions_schema = PackageVersionSchema(many=True)
