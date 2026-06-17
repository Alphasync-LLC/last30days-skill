"""Tests for the shared keyless-Reddit throttle (U4)."""

from unittest import mock

from lib import http, reddit_rss


class TestRateLimiter:
    def test_first_acquire_does_not_sleep(self):
        limiter = http.RateLimiter(min_interval=0.5)
        with mock.patch.object(http.time, "monotonic", return_value=100.0), \
             mock.patch.object(http.time, "sleep") as slept:
            limiter.acquire()
        slept.assert_not_called()

    def test_second_acquire_sleeps_to_maintain_interval(self):
        limiter = http.RateLimiter(min_interval=0.5)
        # First call at t=100, second call 0.1s later -> must wait ~0.4s.
        times = iter([100.0, 100.1, 100.5])
        with mock.patch.object(http.time, "monotonic", side_effect=lambda: next(times)), \
             mock.patch.object(http.time, "sleep") as slept:
            limiter.acquire()
            limiter.acquire()
        slept.assert_called_once()
        waited = slept.call_args.args[0]
        assert abs(waited - 0.4) < 1e-6

    def test_no_sleep_when_interval_already_elapsed(self):
        limiter = http.RateLimiter(min_interval=0.5)
        times = iter([100.0, 102.0])  # 2s gap > interval
        with mock.patch.object(http.time, "monotonic", side_effect=lambda: next(times)), \
             mock.patch.object(http.time, "sleep") as slept:
            limiter.acquire()
            limiter.acquire()
        slept.assert_not_called()


class TestRedditKeylessGetText:
    def test_acquires_limiter_then_delegates(self):
        with mock.patch.object(http.REDDIT_KEYLESS_LIMITER, "acquire") as acq, \
             mock.patch.object(http, "get_text", return_value="body") as gt:
            out = http.reddit_keyless_get_text("https://www.reddit.com/x.rss", accept="application/atom+xml")
        assert out == "body"
        acq.assert_called_once()
        gt.assert_called_once()

    def test_reddit_rss_routes_through_throttle(self):
        # The RSS tier must use the throttled helper, not raw get_text.
        with mock.patch.object(reddit_rss.http, "reddit_keyless_get_text", return_value=None) as throttled:
            reddit_rss.search_rss("test query")
        assert throttled.called
