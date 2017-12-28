from ups.database import Model, db, Column, reference_col, relationship, UuidPrimaryKey

from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from .namespace import Namespace
from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma

from slugify import slugify


class Package(Model, UuidPrimaryKey, SlugMixinFactory('name', nullable=False)):
    __bind_key__ = 'packages'
    __tablename__ = "packages"

    name = Column(db.Unicode(255), nullable=False)

    namespace_slug = reference_col('namespaces', pk_name='slug', nullable=False)
    namespace = relationship(Namespace, backref=db.backref("packages",
                                                           cascade='delete',
                                                           lazy='dynamic'))

    def __init__(self, **kwargs):
        Model.__init__(self, **kwargs)

        if 'namespace' in kwargs:
            self.namespace_slug = kwargs['namespace'].slug

    __table_args__ = (
        UniqueConstraint('namespace_slug', 'slug', name='package_slug_is_unique_in_namespace'),
    )

    @classmethod
    def lookup(cls, namespace, package):
        return (cls.query
                   .filter_by(slug=slugify(package))
                   .filter(Namespace.slug == slugify(namespace))
                   .first())

    @hybrid_property
    def path(self):
        return self.namespace_slug + "/" + self.slug

    @classmethod
    def lookup_path(cls, path):
        return (cls.query.filter_by(path=path).first())

    @classmethod
    def lookup_paths(cls, paths):
        if len(paths) == 0:
            return []

        return cls.query.filter(Package.path.in_(paths)).all()


class PackageSchema(ma.Schema):
    class Meta:
        fields = ("name", "path")


package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)
