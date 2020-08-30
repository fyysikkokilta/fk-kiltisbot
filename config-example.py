"""
This file contains all configuration variables that are needed to by this bot.
"""

# Token that you get from BotFather.
BOT_TOKEN =

# Telegram IDs of people who can run certain priviledged commands.
# #To get id see for example https://t.me/rawdatabot
BOT_ADMINS = []

# ID of chat where daily backup and consumption notifications are sent.
# To get id add https://t.me/rawdatabot to group.
ADMIN_CHAT =

# ID of chat where messages sent to bot are forwarded.
MESSAGING_CHAT =

# ID of Google Sheets where database is backed up. You can get ID from URL
# like this https://docs.google.com/spreadsheets/d/<ID>/some/stuff
INVENTORY_SHEET_ID =
USERS_SHEET_ID =
TRANSACTIONS_SHEET_ID =

# Dictionary that contains calendars to follow as calendar name: calendar
# ID pairs.
GOOGLE_CALENDARS = {
    "FK Tapahtumat": "ahe0vjbi6j16p25rcftgfou5eg@group.calendar.google.com",
    "FK Kokoukset": "guqva296aoq695aqgq68ak7lkc@group.calendar.google.com",
    "FK Fuksit": "u6eju2k63ond2fs7fqvjbna50c@group.calendar.google.com",
    "FK Kulttuuri": "hjhvblcv9n1ue3tf29j3loqqi4@group.calendar.google.com",
    "FK Liikunta": "0orqvov2gidl3m24cnsq4ml1ao@group.calendar.google.com",
    "FK Ura ja opinnot": "ji339ebgiaauv5nk07g41o65q8@group.calendar.google.com"
}

# Base URL to to fiirumi.
FIIRUMI_POSTS_URL = "https://fiirumi.fyysikkokilta.fi/posts.json"
