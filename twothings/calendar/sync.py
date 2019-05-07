'''
Usage:

    Goto https://developers.google.com/calendar/quickstart/python
    Click the "Enable the Google Calendar API" button
    Copy the contents of that file into your clipboard
    $ base64 | keyring set google calsync.credentials
    Paste and Ctrl-D
'''
import glob
import pickle
import base64
import os.path
import hashlib
import logging
import tempfile
from datetime import datetime, timedelta
from urllib.parse import urlparse
from contextlib import contextmanager
from typing import NamedTuple

import keyring

import requests.adapters
from exchangelib import ServiceAccount, Account, CalendarItem, EWSDateTime, \
                        Configuration
from exchangelib.fields import MONDAY, WEDNESDAY
from exchangelib.recurrence import Recurrence, WeeklyPattern
from exchangelib.protocol import BaseProtocol

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from .log import LOGGER

CERT_PATH = os.path.join(os.path.expanduser('~'), '.certs')
if os.path.isdir(CERT_PATH) and list(glob.glob(os.path.join(CERT_PATH, '*'))):
    # An HTTP adapter that uses a custom root CA certificate at a hard coded location
    class RootCAAdapter(requests.adapters.HTTPAdapter):
        def cert_verify(self, conn, url, verify, cert):
            cert_file = {
                os.path.basename(filename): filename \
                for filename in glob.glob(os.path.join(CERT_PATH, '*'))
            }[urlparse(url).hostname]
            super(RootCAAdapter, self).cert_verify(conn=conn, url=url, verify=cert_file, cert=cert)
    # Tell exchangelib to use this adapter class instead of the default
    BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter
else:
    LOGGER.warning('No custom certificates in %r', CERT_PATH)

class CalendarItem(NamedTuple):
    uid: str
    start: datetime
    end: datetime
    location: str
    accepted: bool
    skype: bool

    def __repr__(self):
        return '%s(accepted=%s, skype=%s, start=%s, end=%s, location=%s)' % \
                (self.__class__.__qualname__, self.accepted, self.skype,
                 self.start.isoformat(), self.end.isoformat(), self.location)

    def __str__(self):
        return repr(self)

class PasswordUndefinedError(Exception):
    pass

def keyring_must_get_password(service_name, password):
    password = keyring.get_password(service_name, password)
    if password is None:
        raise PasswordUndefinedError('Could not get %r %r from keyring' \
                                     % (service_name, password,))
    return password

@contextmanager
def keyring_file(service_name, password, must_exist=True):
    with tempfile.NamedTemporaryFile() as fileobj:
        contents = keyring.get_password(service_name, password)
        fileobj.in_keyring = bool(contents is not None)

        # Ensure it exists
        if not fileobj.in_keyring and must_exist:
            raise PasswordUndefinedError('Could not get %r %r from keyring' \
                                         % (service_name, password,))
        if fileobj.in_keyring:
            # Base 64 decode keyring contents and write to fileobj
            fileobj.write(base64.b64decode(contents))
            fileobj.seek(0)

        yield fileobj

        # Encode to base 64 and save to keyring
        fileobj.seek(0)
        contents = base64.b64encode(fileobj.read()).decode('ascii')
        keyring.set_password(service_name, password, contents)

class CalendarSync(object):

    def __init__(self):
        self.logger = LOGGER.getChild(self.__class__.__qualname__)

    def get_ews_calendar_items(self):
        server = keyring_must_get_password('ews', 'server')
        domain = keyring_must_get_password('ews', 'domain')
        ewsid = keyring_must_get_password('ews', 'id')
        email = keyring_must_get_password('ews', 'email')
        password = keyring_must_get_password('ews', 'password')

        credentials = ServiceAccount(domain + '\\' + ewsid, password)
        config = Configuration(server=server, credentials=credentials)
        account = Account(email, credentials=credentials, config=config)

        start = account.default_timezone.localize(EWSDateTime.now())
        end = start + timedelta(weeks=8)

        for i in account.calendar.view(start=start, end=end):
            hash_contents = i.uid + str(i.start) + str(i.end)
            uid = hashlib.sha384(hash_contents.encode('utf-8')).hexdigest()
            yield CalendarItem(uid=uid,
                               start=i.start,
                               end=i.end,
                               location=i.location,
                               accepted=bool(i.my_response_type == 'Accept'),
                               skype=bool(b'skype' in i.mime_content.lower()))

    def calendar_sync_ews_to_google(self):
        ews = {i.uid: i for i in self.get_ews_calendar_items() \
               if i.accepted}

        # If modifying these scopes, delete the file token.pickle.
        SCOPES = ['https://www.googleapis.com/auth/calendar']

        with keyring_file('google', 'calsync.credentials') as creds_file, \
                keyring_file('google', 'calsync.token',
                             must_exist=False) as token:
            creds = None
            if token.in_keyring:
                creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        creds_file.name, SCOPES)
                    creds = flow.run_local_server(port=12982)
                # Save the credentials for the next run
                pickle.dump(creds, token)

            service = build('calendar', 'v3', credentials=creds)

            events_service = service.events()

            # Call the Calendar API
            now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
            events_result = events_service.list(calendarId='primary', timeMin=now,
                                                maxResults=100, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])

            in_google = {event['description']: event for event in events}

            should_not_be_in_google = [v for k, v in in_google.items() \
                                       if not k in ews]
            not_in_google = [v for k, v in ews.items() \
                             if not k in in_google]

            for event in should_not_be_in_google:
                self.logger.info('Removing: start=%s end=%s',
                                  event['start'], event['end'])
                events_service.delete(calendarId='primary',
                                      eventId=event['id']).execute()

            for i in not_in_google:
                event = {
                    'summary': 'Work Meeting (Skype)' if i.skype else \
                               'Work Meeting',
                    'description': i.uid,
                    'location': i.location,
                    'start': {
                        'timeZone': str(i.start.tzinfo),
                        'dateTime': i.start.isoformat(),
                        },
                    'end': {
                        'timeZone': str(i.end.tzinfo),
                        'dateTime': i.end.isoformat(),
                        },
                    'reminders': {
                        'overrides': [
                            {
                                'minutes': 5,
                                'method': 'popup',
                                },
                            {
                                'minutes': 30,
                                'method': 'popup',
                                },
                            ],
                        'useDefault': False,
                        },
                    }
                self.logger.info('Adding: %s', event)
                event = events_service.insert(calendarId='primary',
                                              body=event).execute()

    @classmethod
    def cli(cls):
        logging.basicConfig(level=logging.INFO)
        self = cls()
        self.calendar_sync_ews_to_google()
