from ups.database import Model, db, Column, relationship, reference_col, UuidPrimaryKey
from ups.extensions import marshmallow as ma

from .package_version import PackageVersion, package_version_schema


class ReleasePackage(Model):
    __bind_key__ = 'packages'
    __tablename__ = "releases_packages"

    package_id = reference_col('packages', nullable=True)
    release_id = reference_col('releases', nullable=False)
    package_version_id = reference_col('package_versions', nullable=False)

    release = relationship('Release', backref='release_packages', uselist=False)
    package = relationship('Package', backref='release_packages', uselist=False)
    package_version = relationship('PackageVersion', backref='release_packages', uselist=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.package_id is None:
            version = kwargs.get('package_version') or PackageVersion.get(self.package_version_id)
            self.package_id = version.package_id

    __table_args__ = (
        db.UniqueConstraint('package_id', 'release_id'),
        db.PrimaryKeyConstraint('package_version_id', 'release_id'),
    )

    def __repr__(self):
        return self.repr(['package_version_id', 'release_id'])


class Release(Model, UuidPrimaryKey):
    __bind_key__ = 'packages'
    __tablename__ = "releases"

    title = Column(db.Unicode)

    packages = relationship('Package', secondary="releases_packages",
                            backref='releases', viewonly=True)

    package_versions = relationship('PackageVersion',
                                    secondary="releases_packages",
                                    backref='releases',
                                    viewonly=True)

    def set_versions(self, versions=[], commit=False):
        self.release_packages = [ReleasePackage(release=self, package_version=v)
                                 for v in versions]

        self.save(commit=commit)


class ReleaseManifestSchema(ma.Schema):
    class Meta:
        fields = ("title", "package_versions")

    package_versions = ma.Nested(package_version_schema, many=True, dump_to="packages")


release_manifest_schema = ReleaseManifestSchema()
release_manifests_schema = ReleaseManifestSchema(many=True)
