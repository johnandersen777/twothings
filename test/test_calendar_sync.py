import unittest

from twothings.calendar.sync import CalendarSync

class TestCalendarSync(unittest.TestCase):

    def test_calendar_sync_ews_to_google(self):
        calendar_sync = CalendarSync()
        calendar_sync.calendar_sync_ews_to_google()
