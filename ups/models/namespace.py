from ups.database import Model, db, Column

from .utils import SlugMixinFactory
from ups.extensions import marshmallow as ma


class Namespace(Model,
                SlugMixinFactory('name', nullable=False, unique=True, primary_key=True)):
    __bind_key__ = 'packages'
    __tablename__ = "namespaces"

    name = Column(db.Unicode(255), nullable=False, unique=True)


class NamespaceSchema(ma.Schema):
    class Meta:
        fields = ("name", "slug")


namespace_schema = NamespaceSchema()
namespaces_schema = NamespaceSchema(many=True)
