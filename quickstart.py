"""
This script fetches events from Guild of Physics calendars using Google's Calendar API
and returns them in a list. 
"""

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# 977281388397-97gft1pbtps80pt5ak4kglfugpl07af3.apps.googleusercontent.com
# QUBMT1x38caSB7MgZSHVBN9w
calendars = {
    "FK Tapahtumat": "ahe0vjbi6j16p25rcftgfou5eg@group.calendar.google.com",
    "FK Kokoukset": "guqva296aoq695aqgq68ak7lkc@group.calendar.google.com",
    "FK Fuksit": "u6eju2k63ond2fs7fqvjbna50c@group.calendar.google.com",
    "FK Kulttuuri": "hjhvblcv9n1ue3tf29j3loqqi4@group.calendar.google.com",
    "FK Liikunta": "0orqvov2gidl3m24cnsq4ml1ao@group.calendar.google.com",
    "FK Ura ja opinnot": "ji339ebgiaauv5nk07g41o65q8@group.calendar.google.com"
}

all = {}

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('calendar_token.pickle'):
        with open('calendar_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('calendar_token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().today().isoformat() + 'Z' # 'Z' indicates UTC time

    for x,y in calendars.items():

        all_events = []
        events_result = service.events().list(calendarId=y, timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            all_events.append(['Ei tulevia tapahtumia'])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))[:10]
            #print(start, event['summary'], event["htmlLink"])
            all_events.append([start, event["summary"], event["htmlLink"]])

        all[x] = all_events
    return all

if __name__ == '__main__':
    main()
