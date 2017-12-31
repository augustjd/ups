from ups.database import Model, db, Column

from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma

from slugify import slugify


class Package(Model, SlugMixinFactory('name', nullable=False, unique=True, primary_key=True)):
    __bind_key__ = 'packages'
    __tablename__ = "packages"

    name = Column(db.Unicode(255), nullable=False, unique=True)

    @classmethod
    def lookup_slugs(cls, slugs):
        if len(slugs) == 0:
            return []

        slugs = [slugify(p) for p in slugs]

        return cls.query.filter(Package.slug.in_(slugs)).all()


class PackageSchema(ma.Schema):
    class Meta:
        fields = ("name", "slug")


package_schema = PackageSchema()
packages_schema = PackageSchema(many=True)
