from ups.database import Model, db, Column, reference_col, relationship

from .package import packages_schema
from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma


class Suite(Model,
            SlugMixinFactory('name', nullable=False, unique=True, primary_key=True)):
    """A group of packages."""
    __bind_key__ = 'packages'
    __tablename__ = "suites"

    name = Column(db.Unicode(255), nullable=False, unique=True)

    packages = relationship('Package', secondary='suite_packages',
                            backref=db.backref('suites'))


class SuiteSchema(ma.Schema):
    class Meta:
        fields = ("name", "slug", "packages")

    packages = ma.Nested(packages_schema, many=True)


suite_schema = SuiteSchema()
suites_schema = SuiteSchema(many=True)


class SuitePackage(Model):
    __bind_key__ = 'packages'
    __tablename__ = "suite_packages"

    package_id = reference_col('packages', nullable=False, pk_name="slug")
    suite_id = reference_col('suites', nullable=False, pk_name="slug")

    suite = relationship('Suite', uselist=False)
    package = relationship('Package', uselist=False)

    __table_args__ = (
        db.PrimaryKeyConstraint('package_id', 'suite_id'),
    )

    def __repr__(self):
        return self.repr(['package_id', 'suite_id'])
