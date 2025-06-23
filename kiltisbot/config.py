"""
Configuration loader that reads from environment variables.
This replaces the old config.py file that contained hardcoded values.
"""

import os
from typing import List, Dict


def get_env_list(key: str, default: List[int] = None) -> List[int]:
    """Get a list of integers from an environment variable."""
    if default is None:
        default = []
    value = os.getenv(key)
    if not value:
        return default
    try:
        return [int(x.strip()) for x in value.split(",") if x.strip()]
    except ValueError:
        return default


# Token that you get from BotFather.
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Telegram IDs of people who can run certain priviledged commands.
BOT_ADMINS = get_env_list("BOT_ADMINS")

# ID of chat where daily backup and consumption notifications are sent.
ADMIN_CHAT = os.getenv("ADMIN_CHAT")

# ID of chat where messages sent to bot are forwarded.
MESSAGING_CHAT = os.getenv("MESSAGING_CHAT")

# ID of Google Sheets where database is backed up.
INVENTORY_SHEET_ID = os.getenv("INVENTORY_SHEET_ID")
USERS_SHEET_ID = os.getenv("USERS_SHEET_ID")
TRANSACTIONS_SHEET_ID = os.getenv("TRANSACTIONS_SHEET_ID")

# Dictionary that contains calendars to follow as calendar name: calendar ID pairs.
GOOGLE_CALENDARS: Dict[str, str] = {
    "FK Tapahtumat": os.getenv("GOOGLE_CALENDAR_FK_TAPAHTUMAT", "ahe0vjbi6j16p25rcftgfou5eg@group.calendar.google.com"),
    "FK Kokoukset": os.getenv("GOOGLE_CALENDAR_FK_KOKOUKSET", "guqva296aoq695aqgq68ak7lkc@group.calendar.google.com"),
    "FK Fuksit": os.getenv("GOOGLE_CALENDAR_FK_FUKSIT", "u6eju2k63ond2fs7fqvjbna50c@group.calendar.google.com"),
    "FK Kulttuuri": os.getenv("GOOGLE_CALENDAR_FK_KULTTUURI", "hjhvblcv9n1ue3tf29j3loqqi4@group.calendar.google.com"),
    "FK Liikunta": os.getenv("GOOGLE_CALENDAR_FK_LIIKUNTA", "0orqvov2gidl3m24cnsq4ml1ao@group.calendar.google.com"),
    "FK Ura ja opinnot": os.getenv(
        "GOOGLE_CALENDAR_FK_URA_JA_OPINNOT", "ji339ebgiaauv5nk07g41o65q8@group.calendar.google.com"
    ),
}

# Base URL to fiirumi.
FIIRUMI_POSTS_URL = os.getenv("FIIRUMI_POSTS_URL", "https://fiirumi.fyysikkokilta.fi")


def validate_config():
    """Validate that all required environment variables are set."""
    required_vars = [
        "BOT_TOKEN",
        "ADMIN_CHAT",
        "MESSAGING_CHAT",
        "INVENTORY_SHEET_ID",
        "USERS_SHEET_ID",
        "TRANSACTIONS_SHEET_ID",
    ]

    missing_vars = []
    for var in required_vars:
        if not globals().get(var):
            missing_vars.append(var)

    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")


# Validate configuration on import
validate_config()
