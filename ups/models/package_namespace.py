from ups.database import Model, db, Column

from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma


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
