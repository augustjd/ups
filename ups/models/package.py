from ups.database import Model, db, Column, reference_col, relationship, UuidPrimaryKey

from sqlalchemy.schema import UniqueConstraint

from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma

from slugify import slugify


class PackageNamespace(Model,
                       SlugMixinFactory('name', nullable=False, unique=True, primary_key=True)):
    __bind_key__ = 'packages'
    __tablename__ = "package_namespaces"

    name = Column(db.Unicode(255), nullable=False, unique=True)


class PackageNamespaceSchema(ma.Schema):
    class Meta:
        fields = ("name",)


package_namespace_schema = PackageNamespaceSchema()
package_namespaces_schema = PackageNamespaceSchema(many=True)


class Package(Model, UuidPrimaryKey, SlugMixinFactory('name', nullable=False)):
    __bind_key__ = 'packages'
    __tablename__ = "packages"

    name = Column(db.Unicode(255), nullable=False)

    namespace_slug = reference_col('package_namespaces', pk_name='slug', nullable=False)
    namespace = relationship(PackageNamespace, backref=db.backref("packages",
                                                                  cascade='delete',
                                                                  lazy='dynamic'))

    __table_args__ = (
        UniqueConstraint('namespace_slug', 'slug', name='package_slug_is_unique_in_namespace'),
    )

    @classmethod
    def lookup(cls, namespace, package):
        return (cls.query
                   .filter_by(slug=slugify(package))
                   .filter(PackageNamespace.slug == slugify(namespace))
                   .first())


class PackageSchema(ma.Schema):
    class Meta:
        fields = ("name",)


package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)
