from django.test import TestCase

from ..utils import format_elapsed_time


class FormatElapsedTimeTest(TestCase):
    def test_format_elapsed_time_seconds(self):
        """Test formatting of seconds only"""
        result = format_elapsed_time(45.123)
        self.assertEqual(result, '0h:0m:45.123s')

    def test_format_elapsed_time_minutes(self):
        """Test formatting of minutes and seconds"""
        result = format_elapsed_time(125.456)
        self.assertEqual(result, '0h:2m:5.456s')

    def test_format_elapsed_time_hours(self):
        """Test formatting of hours, minutes and seconds"""
        result = format_elapsed_time(3725.789)
        self.assertEqual(result, '1h:2m:5.789s')

    def test_format_elapsed_time_zero(self):
        """Test formatting of zero time"""
        result = format_elapsed_time(0.0)
        self.assertEqual(result, '0h:0m:0.000s')