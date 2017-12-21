# -*- coding: utf-8 -*-
"""User models."""

import enum

from flask_login import UserMixin
from sqlalchemy import and_
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy_utils import ChoiceType

from ups.database import (Column, Model, UuidPrimaryKey, db)
from ups.extensions import bcrypt


class UserType(enum.Enum):
    Customer      = 0b00000001             # noqa - ordinary user of the app
    Trainer       = 0b00000011             # noqa - a personal trainer
    Workstation   = 0b00000100             # noqa - a SmartSpot Workstation
    GymOwner      = 0b00001000 | Trainer   # noqa - an owner of a partner gym
    Partner       = 0b00010000 | GymOwner  # noqa - a partner gym chain, e.g. LikingFit
    Administrator = 0b00111111             # noqa - a SmartSpot employee


class User(UserMixin, UuidPrimaryKey, Model):
    """A user of the app."""

    __bind_key__ = 'users'
    __tablename__ = 'users'

    email = Column(db.String(80), unique=True, nullable=True)
    username = Column(db.Unicode(80), unique=True, nullable=False)
    social_id = Column(db.String(80), unique=True, nullable=True)

    password = Column(db.String(256), nullable=True)

    active = Column(db.Boolean(), default=True, nullable=False)

    user_type = Column(ChoiceType(UserType, impl=db.Integer()),
                       nullable=False,
                       default=UserType.Customer)

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, value):
        """Check password."""
        if self.password is None or value is None:
            return False
        return bcrypt.check_password_hash(self.password, value)

    @classmethod
    def username_taken(cls, username):
        return cls.query.filter(User.username.ilike(username)).count() > 0

    @classmethod
    def email_taken(cls, email):
        return cls.query.filter(User.email.ilike(email)).count() > 0

    @hybrid_method
    def has_role(self, role):
        return self.user_type.value >= role.value and self.user_type.value & role.value

    @has_role.expression
    def has_role(cls, role):
        return and_(cls.user_type >= role, cls.user_type.op('&')(role) > 0)
