"""
Tests for the cleaning pipeline.
"""

from src.analysis.cleaning import (
    clean_text,
    detect_neighborhoods,
    detect_phase,
    flag_quality,
    tokenize_simple,
)


class TestCleanText:
    def test_strips_urls(self):
        text = "Check this out https://example.com/page and www.test.com"
        result = clean_text(text)
        assert "https://" not in result
        assert "www." not in result

    def test_strips_usernames(self):
        assert "@user123" not in clean_text("Thanks @user123 for sharing")
        assert "u/reddituser" not in clean_text("As u/reddituser said")

    def test_strips_deleted(self):
        assert "[deleted]" not in clean_text("[deleted] was here")
        assert "[removed]" not in clean_text("This was [removed]")

    def test_hashtag_to_word(self):
        result = clean_text("Love #SouthShore community")
        assert "SouthShore" in result
        assert "#" not in result

    def test_empty_input(self):
        assert clean_text("") == ""
        assert clean_text(None) == ""


class TestTokenize:
    def test_basic(self):
        tokens = tokenize_simple("Hello World!")
        assert tokens == ["hello", "world"]

    def test_empty(self):
        assert tokenize_simple("") == []


class TestDetectPhase:
    def test_pre_phase(self):
        assert detect_phase("2025-09-20T12:00:00+00:00") == "pre"

    def test_event_phase(self):
        assert detect_phase("2025-09-30T12:00:00+00:00") == "event"

    def test_post_week1(self):
        assert detect_phase("2025-10-03T12:00:00+00:00") == "post_week1"

    def test_out_of_window(self):
        assert detect_phase("2025-12-01T12:00:00+00:00") == "out_of_window"


class TestDetectNeighborhoods:
    def test_south_shore(self):
        hoods = detect_neighborhoods("The raid happened in South Shore near 71st")
        assert "South Shore" in hoods

    def test_multiple(self):
        hoods = detect_neighborhoods("South Shore and Woodlawn are affected")
        assert "South Shore" in hoods
        assert "Woodlawn" in hoods

    def test_no_match(self):
        assert detect_neighborhoods("Random text with no neighborhood") == []


class TestFlagQuality:
    def test_ok(self):
        assert flag_quality("This is a normal post about the community", 8) == "ok"

    def test_short(self):
        assert flag_quality("Hi", 1) == "short"

    def test_spam(self):
        assert flag_quality("Buy now http://a http://b http://c http://d", 6) == "spam"
