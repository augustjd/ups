from tests.factories import Factories

import arrow


class TestScheduledReleases(Factories):
    def test_schedule_release_updates_current(self, suite, suite_release):
        assert suite.current_release() is None

        scheduled_release = suite_release.schedule(arrow.utcnow().shift(minutes=-1), commit=True)
        assert scheduled_release is not None
        assert scheduled_release.release == suite_release

        assert suite.current_release() == suite_release

    def test_schedule_release_in_future_does_not_update_current(self, suite, suite_release):
        assert suite.current_release() is None

        scheduled_release = suite_release.schedule(arrow.utcnow().shift(hours=1),
                                                   commit=True)
        assert scheduled_release is not None
        assert scheduled_release.release == suite_release

        current_release = suite.current_release()
        assert current_release is None  # won't not be None for 1 hr
