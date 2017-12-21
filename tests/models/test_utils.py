from sqlalchemy import not_

from ups.models.utils import TimezoneAwareDatetime
from ups.database import Model, Column, UuidPrimaryKey

import arrow
import datetime


class Example(Model, UuidPrimaryKey):
    __bind_key__ = 'packages'
    __tablename__ = 'example'

    created = Column(TimezoneAwareDatetime, default=arrow.utcnow)


class TestTimezoneAwareDatetime:
    def test_arrow_date_is_utc_by_default(self, app):
        dt = arrow.utcnow().shift(seconds=-1)
        e = Example(created=dt)
        e.save()

        assert e.created.date() == dt.date()

        assert Example.query.filter(Example.created.date() == dt.date()).all() == [e]
        assert Example.query.filter(Example.created.date() != dt.date()).all() == []

    def test_arrow_date_specify_timezone(self, app):
        dt = arrow.get('2013-05-11T00:00:00+00:00')
        e = Example(created=dt)
        e.save()

        expected = datetime.date(2013, 5, 11)
        assert dt.date() == expected

        assert Example.query.filter(Example.created.date() == expected).all() == [e]

        # in 'US/Pacific', midnight UTC 2013-05-11 is actually 2013-05-10 (since it's -8:00).

        us_pacific_date = datetime.date(2013, 5, 10)
        assert Example.query.filter(
            Example.created.date(tz='US/Pacific') == us_pacific_date).all() == [e]

    def test_arrow_date_is_past(self, app):
        dt = arrow.utcnow().shift(seconds=-1)
        e = Example(created=dt)
        e.save()

        assert Example.query.filter(Example.created.is_past()).all() == [e]
        assert Example.query.filter(not_(Example.created.is_past())).all() == []

    def test_arrow_date_is_future(self, app):
        dt = arrow.utcnow().shift(seconds=-1)
        e = Example(created=dt)
        e.save()

        assert Example.query.filter(not_(Example.created.is_future())).all() == [e]
        assert Example.query.filter(Example.created.is_future()).all() == []
