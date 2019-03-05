from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import db
import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar.readonly']

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



def import_inventory():
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TUOTTEET, range="A1:3", majorDimension = "COLUMNS").execute()
    values = result.get('values', [])
    values = list(map(lambda x: [x[0], int(x[1]), int(x[2])], values[1:]))

    print(values)
    db.delete_inventory()
    for i in values:
        db.add_item(i[0], i[1], i[2])
    return len(values)

def import_users():
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=KAYTTAJAT, range="A1:D", majorDimension = "ROWS").execute()
    values = result.get('values', [])
    values = list(map(lambda x: [x[0], x[1], x[2], int(x[3])], values))

    users = len(db.get_users())
    print(values)
    db.delete_users()
    for i in values:
        db.add_user(i[0], i[1], i[2], i[3])

    return len(db.get_users()) - users

def import_transactions():
    service = build('sheets', 'v4', credentials=creds)

    return

def export_inventory():
    service = build('sheets', 'v4', credentials=creds)

    inventory = list(map(lambda x: str(x[0]), db.get_stocks()))

    print(inventory)
    values = [[datetime.datetime.today().isoformat()[:16]] + inventory]

    body = {"values": values}

    result = service.spreadsheets().values().append(
    spreadsheetId=TUOTTEET, range="A1:A",
    valueInputOption="RAW", body=body).execute()


def export_users():
    service = build('sheets', 'v4', credentials=creds)

    date = datetime.datetime.today().isoformat()[:16].replace(":", ".")

    users = list(map(lambda x: [str(i) for i in x], db.get_users()))

    requests = []
    requests.append({
      "addSheet": {
        "properties": {
          "title": date,
          "index": 0
        }
      }
    })

    add_body = {"requests": requests}
    body = {"values": users}

    response = service.spreadsheets().batchUpdate(
    spreadsheetId=KAYTTAJAT,
    body=add_body).execute()

    result = service.spreadsheets().values().append(
    spreadsheetId=KAYTTAJAT, range= date + "!A1",
    valueInputOption="RAW", body=body).execute()

    return len(users)

def export_transactions():
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=TAPAHTUMAT, range="A1:A").execute()
    values = result.get('values', [])

    end = 0
    if len(values) > 1:
        end = int(values[-1][0])

    trans = db.get_transactions_after(end)

    mapped = list(map(lambda x: [str(i) for i in x], trans))

    body = {"values": mapped}

    result = service.spreadsheets().values().append(
    spreadsheetId=TAPAHTUMAT, range="A1:A",
    valueInputOption="RAW", body=body).execute()

    return len(trans)


def main():
    import_inventory()
    export_transactions()

if __name__ == '__main__':
    main()
