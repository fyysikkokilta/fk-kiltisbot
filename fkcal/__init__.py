"""This file handles getting the events from the Guild of Physics
Google calendar using Google's calendar API. If user don't have
required credentials browser opens and user can sign in to Google
to create them."""

from __future__ import print_function
import datetime
import pickle
import os.path
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# TODO consider moving these to config
calendars = {
    "FK Tapahtumat": "ahe0vjbi6j16p25rcftgfou5eg@group.calendar.google.com",
    "FK Kokoukset": "guqva296aoq695aqgq68ak7lkc@group.calendar.google.com",
    "FK Fuksit": "u6eju2k63ond2fs7fqvjbna50c@group.calendar.google.com",
    "FK Kulttuuri": "hjhvblcv9n1ue3tf29j3loqqi4@group.calendar.google.com",
    "FK Liikunta": "0orqvov2gidl3m24cnsq4ml1ao@group.calendar.google.com",
    "FK Ura ja opinnot": "ji339ebgiaauv5nk07g41o65q8@group.calendar.google.com"
}


def get_events():
    """ Prints the start and name of the next 10 events on the user's calendar."""

    all_calendar_events = {}
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

    # Suppress warning in logs
    # https://github.com/googleapis/google-api-python-client/issues/299
    service = build('calendar', 'v3', credentials=creds, cache_discovery=False)

    now = datetime.datetime.utcnow().today().isoformat() + 'Z' # 'Z' indicates UTC time

    for calendar_name, calendar_id in calendars.items():
        all_events = []
        events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            all_events.append(['Ei tulevia tapahtumia'])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))[:10]
            all_events.append([start, event["summary"], event["htmlLink"]])
        all_calendar_events[calendar_name] = all_events

    return all_calendar_events


def tapahtumat(bot, update):
    """Return all_calendar_events events in all_calendar_events calendars."""

    text = ""
    events = get_events()
    for calendar_name, calendar_events in events.items():
        text += f"\n*{calendar_name}*\n"
        for event in calendar_events:
            if len(event) == 1:
                text += f"{event[0]}\n"
            else:
                text += f"{'.'.join(event[0].split('-')[::-1])} [{event[1]}]({event[2]})\n"
    bot.send_message(update.effective_chat.id, text, parse_mode="MARKDOWN")


def tapahtumat_tanaan():
    """Return list of events ocurring today."""

    events = get_events()
    tanaan = datetime.datetime.today().isoformat()[:10]
    out = []
    for _, calendar_events in events.items():
        out += [event for event in calendar_events if event[0] == tanaan]

    return out


def tanaan_command(bot, update):
    """Send message containing list of todays events."""

    text = ""
    events = tapahtumat_tanaan()
    if events:
        events_parsed = [f"<a href=\"{event[2]}\">{event[1]}</a>\n" for event in events]
        text = "<b>TÄNÄÄN:</b>\n" + events_parsed.join()
    else:
        text = "<b>TÄNÄÄN</b> ei ole tapahtumia"
    bot.send_message(update.effective_chat.id, text, parse_mode="HTML")


def tanaan_text(bot, update):
    """Reacts to chat messages containing string "tänään" if there are events today
    by sending list of events today."""

    events = tapahtumat_tanaan()
    if events and "tänään" in update.effective_message.text.lower():
        text = ""
        events_parsed = [f"<a href=\"{event[2]}\">{event[1]}</a>\n" for event in events]
        text = "<b>TÄNÄÄN:</b>\n" + events_parsed.join()
        bot.send_message(update.effective_chat.id, text, parse_mode="HTML")
