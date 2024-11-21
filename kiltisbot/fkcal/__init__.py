"""
This file handles getting the events from the Guild of Physics
Google calendar using Google's calendar API.
"""

import datetime

from googleapiclient.discovery import build
from telegram import Update
from ..utils import CallbackContext

import config
from kiltisbot import google_auth


def get_events():
    """Prints the start and name of the next 10 events on the user's calendar."""

    all_calendar_events = {}

    # Suppress warning in logs
    # https://github.com/googleapis/google-api-python-client/issues/299
    service = build("calendar", "v3", credentials=google_auth.creds, cache_discovery=False)

    now = datetime.datetime.utcnow().today().isoformat() + "Z"  # 'Z' indicates UTC time

    for calendar_name, calendar_id in config.GOOGLE_CALENDARS.items():
        all_events = []
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
        if not events:
            all_events.append(["Ei tulevia tapahtumia"])
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))[:10]
            all_events.append([start, event["summary"], event["htmlLink"]])
        all_calendar_events[calendar_name] = all_events

    return all_calendar_events


async def tapahtumat(update: Update, context: CallbackContext):
    """Return all_calendar_events events in all_calendar_events calendars."""
    assert update.effective_chat is not None, "Update unexpectedly has no chat"
    text = ""
    events = get_events()
    for calendar_name, calendar_events in events.items():
        text += f"\n*{calendar_name}*\n"
        for event in calendar_events:
            if len(event) == 1:
                text += f"{event[0]}\n"
            else:
                text += f"{'.'.join(event[0].split('-')[::-1])} [{event[1]}]({event[2]})\n"
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="MARKDOWN", disable_web_page_preview=True)


def tapahtumat_tanaan():
    """Return list of events ocurring today."""

    events = get_events()
    tanaan = datetime.datetime.today().isoformat()[:10]  # YYYY-MM-DD
    out = []
    for _, calendar_events in events.items():
        out += [event for event in calendar_events if event[0] == tanaan]

    return out


async def tanaan_command(update: Update, context: CallbackContext):
    """Send message containing list of todays events."""
    assert update.effective_chat is not None, "Update unexpectedly has no chat"

    text = ""
    events = tapahtumat_tanaan()
    if events:
        events_parsed = [f'<a href="{event[2]}">{event[1]}</a>\n' for event in events]
        text = "<b>TÄNÄÄN:</b>\n" + "\n".join(events_parsed)
    else:
        text = "<b>TÄNÄÄN</b> ei ole tapahtumia"
    await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", disable_web_page_preview=True)


async def tanaan_text(update: Update, context: CallbackContext):
    """Reacts to chat messages containing string "tänään" if there are events today
    by sending list of events today."""
    assert update.effective_chat is not None, "Update unexpectedly has no chat"
    assert update.effective_message is not None, "Update unexpectedly has no message"
    assert update.effective_message.text is not None, "Update message unexpectedly has no text"

    events = tapahtumat_tanaan()
    if events and "tänään" in update.effective_message.text.lower():
        text = ""
        events_parsed = [f'<a href="{event[2]}">{event[1]}</a>\n' for event in events]
        text = "<b>TÄNÄÄN:</b>\n" + "\n".join(events_parsed)
        await context.bot.send_message(update.effective_chat.id, text, parse_mode="HTML", disable_web_page_preview=True)
