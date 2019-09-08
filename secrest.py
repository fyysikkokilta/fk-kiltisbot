"""
This file contains Telegram bot tokens and Google sheet codes etc.
"""

def bot_token(env):
    """
    Returns the Telegram bot token for either "PROD" or "TEST"
    """

    if env == 'TEST':
        #Bot token for the test bot
        return "795847607:AAFVVYCqMnULe22gDNlQjPVMzCcxibKWric"
    else:
        #Bot token for the production bot
        return "647159337:AAFmV4Rf5tJ5nTdWHUEa1qFH1yxzK10r4PE"
        
def chat_code(env):
    """
    Returns the Telegram chat id for either "PROD" or "TEST"
    """

    if env == 'TEST':
        #Chat id for the test chat
        return -393042631
    else:
        #Chat id for the test chat
        return -386083933

def database_name(env):
    if env == 'TEST':
        #Chat id for the test chat
        return "kiltis_test.db"
    else:
        #Chat id for the test chat
        return "kiltis.db"


def google_sheets(env):
    """
    Returns the Sheet id's fot the Google Drive backend.
    """

    if env == 'TEST':
        #The sheet id's for the test sheets
        return {"TUOTTEET": "1b_F2DGilrzGjarqEbsFE5_RW-lrIuBm-MRFDxFo5FrA",
                "TAPAHTUMAT": "19Vce226X9xDl6jmXsAMhBuai5My_JskOagRHtMjRaxk",
                "KAYTTAJAT": "1loeQ1UV_B8luNCQjN7N-sxPrnCVEj13MfGBpXIfDJ7Q"}
    else:
        #Sheet id's for the production sheets
        return {"TUOTTEET": "1m9mqzS0Vw1qepTOvIJXIJLCzgWwsWZyYz-8iISGD4PY",
                "TAPAHTUMAT": "1y-zFM-3GE44BLpv4O6TOfU_o6Mtu9ZwyfGWQhCZ7WoE",
                "KAYTTAJAT": "1DYq5i7HDH4_5WkjF92pwEA8fb-woAY5wh5bCwMUIp8w"}