from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import db

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/calendar.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
SAMPLE_RANGE_NAME = 'Class Data!A1:C'

TUOTTEET = "1m9mqzS0Vw1qepTOvIJXIJLCzgWwsWZyYz-8iISGD4PY"
TAPAHTUMAT = "1y-zFM-3GE44BLpv4O6TOfU_o6Mtu9ZwyfGWQhCZ7WoE"
KAYTTAJAT = "1DYq5i7HDH4_5WkjF92pwEA8fb-woAY5wh5bCwMUIp8w"

creds = None

# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
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
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)


def import_inventory():
    global service

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TUOTTEET,
                                range="A1:C").execute()
    values = result.get('values', [])


    values = list(map(lambda x: [x[0], int(x[1]), int(x[2])], values[1:]))

    db.delete_inventory()

    for i in values:
        db.add_item(i[0], i[1], i[2])




def main():
    import_inventory()

if __name__ == '__main__':
    main()
