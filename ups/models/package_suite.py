from ups.database import Model, db, Column, reference_col, relationship

from .package import packages_schema
from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma


class PackageSuite(Model,
                   SlugMixinFactory('name', nullable=False, unique=True, primary_key=True)):
    """A group of packages."""
    __bind_key__ = 'packages'
    __tablename__ = "package_suites"

    name = Column(db.Unicode(255), nullable=False, unique=True)

    packages = relationship('Package', secondary='suite_packages',
                            backref=db.backref('suites'))


class PackageSuiteSchema(ma.Schema):
    class Meta:
        fields = ("name", "slug", "packages")

    packages = ma.Nested(packages_schema, many=True)


package_suite_schema = PackageSuiteSchema()
package_suites_schema = PackageSuiteSchema(many=True)


class SuitePackage(Model):
    __bind_key__ = 'packages'
    __tablename__ = "suite_packages"

    package_id = reference_col('packages', nullable=False)
    suite_id = reference_col('package_suites', nullable=False, pk_name="slug")

    suite = relationship('PackageSuite', uselist=False)
    package = relationship('Package', uselist=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('package_id', 'suite_id'),
    )

    def __repr__(self):
        return self.repr(['package_id', 'suite_id'])
