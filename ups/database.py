# -*- coding: utf-8 -*-
"""Database module, including the SQLAlchemy database object and DB-related utilities."""
import uuid

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_utils import UUIDType

from sqlalchemy import func
from sqlalchemy.orm import Query, relationship
from sqlalchemy.orm.attributes import flag_modified, set_attribute


class CustomQuery(Query):
    def all_scalar(self):
        results = self.all()

        if results:
            return [r for (r,) in results]
        else:
            return []

    def to_sql(self):
        """Return a literal SQL representation of the query."""
        dialect = self.session.bind.dialect
        return str(self.statement.compile(dialect=dialect))


db = SQLAlchemy(session_options={'query_cls': CustomQuery})


# Alias common SQLAlchemy names
Column = db.Column
relationship = relationship


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete) operations."""

    @classmethod
    def all(cls, *args, **kwargs):
        if len(args) == 1 and kwargs == {}:
            return cls.query.filter_by(id=args[0]).all()
        else:
            return cls.query.filter_by(**kwargs).all()

    @classmethod
    def get(cls, *args, **kwargs):
        """Get this model by id or filter by kwargs."""
        if len(args) == 1 and kwargs == {}:
            return cls.query.get(args[0])
        elif 'id' in kwargs:
            return cls.query.get(kwargs['id'])
        else:
            return cls.query.filter_by(**kwargs).first()

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.items():
            set_attribute(self, attr, value)
            if attr in self.__table__.columns:
                flag_modified(self, attr)

        if commit:
            return self.save()
        else:
            return self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return self

    @classmethod
    def save_all(cls, objects, commit=True):
        if commit:
            cls.query.session.bulk_save_objects(objects)  # DB
        else:
            db.session.add_all(objects)

        return objects

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base model class that includes CRUD convenience methods."""

    __abstract__ = True

    def repr(self, columns=[]):
        kv = []

        for column in columns:
            value = getattr(self, column)

            if type(value) is uuid.UUID:
                s = str(value)
            elif type(value) is str and value.startswith('http'):
                s = f"({value})"
            else:
                s = repr(value)

            kv.append((column, s))

        column_str = ", ".join("{}={}".format(k, v) for k, v in kv)

        return "<{}({})>".format(self.__class__.__name__, column_str)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.repr([self.__primary_key__])

    @classmethod
    def random(cls, n=1):
        if n == 1:
            return cls.query.order_by(func.random()).first()
        else:
            return cls.query.order_by(func.random()).limit(n).all()


class UuidPrimaryKey(object):
    """A mixin that adds a surrogate uuid 'primary key' column named ``id``
    to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    __primary_key__ = 'id'

    id = db.Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)

    @classmethod
    def generate_example_pk(cls):
        return cls.id.default.arg(None)


class IntPrimaryKey(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id``
    to any declarative-mapped class."""

    __table_args__ = {'extend_existing': True}

    __primary_key__ = 'id'

    id = db.Column(db.Integer, primary_key=True)


def reference_col(tablename, nullable=False, pk_name='id', **kwargs):
    """Column that adds primary key foreign key reference.

    Usage: ::

        category_id = reference_col('category')
        category = relationship('Category', backref='categories')
    """
    return db.Column(
        db.ForeignKey('{0}.{1}'.format(tablename, pk_name)),
        nullable=nullable, **kwargs)
