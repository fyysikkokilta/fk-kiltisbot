"""This file implements all the Google Sheets backend features for the tab."""

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import db
import datetime
import settings

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/calendar.readonly']

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
    result = sheet.values().get(spreadsheetId=settings.secrets["sheets"]["tuotteet"], range="A1:3", majorDimension = "COLUMNS").execute()
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
    result = sheet.values().get(spreadsheetId=settings.secrets["sheets"]["kayttajat"], range="A1:D", majorDimension = "ROWS").execute()
    values = result.get('values', [])
    values = list(map(lambda x: [x[0], x[1], x[2], int(x[3])], values))

    users = len(db.get_users())
    print(values)

    export_users() #safety export to not lose data

    db.delete_users()
    for i in values:
        db.add_user(i[0], i[1], i[2], i[3])

    return len(db.get_users()) - users

def import_transactions():
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=settings.secrets["sheets"]["tapahtumat"], range="A1:F").execute()["values"]
    print(result[:10])
    values = list(map(lambda x: (int(x[1]), x[3], x[5], int(float(x[4]))), result[1:]))
    print(values[:10])
    #values = list(map(lambda x: (x[1], x[3], x[5], x[4]), result))

    db.delete_transactions()

    for i in values:
        try: 
            db.add_transaction(int(i[0]), None, i[1], i[2], int(i[3]))
        except:
            pass
            #print(i)

    return len(values)

def export_inventory():
    service = build('sheets', 'v4', credentials=creds)

    inventory = list(map(lambda x: str(x[0]), db.get_stocks()))

    print(inventory)
    values = [[datetime.datetime.today().isoformat()[:16]] + inventory]

    body = {"values": values}

    result = service.spreadsheets().values().append(
        spreadsheetId=settings.secrets["sheets"]["tuotteet"], range="A1:A",
        valueInputOption="RAW", body=body).execute()


def export_users():
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
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

    sheets = sheet.get(spreadsheetId=settings.secrets["sheets"]["kayttajat"]).execute()["sheets"]
    horizon = (datetime.datetime.today() - datetime.timedelta(days = 30)).isoformat()

    for i in sheets:
        if i["properties"]["title"] < horizon:
            requests.append({"deleteSheet": {"sheetId": i["properties"]["sheetId"]}})

    add_body = {"requests": requests}
    body = {"values": users}

    response = service.spreadsheets().batchUpdate(
    spreadsheetId=settings.secrets["sheets"]["kayttajat"],
    body=add_body).execute()

    result = service.spreadsheets().values().append(
    spreadsheetId=settings.secrets["sheets"]["kayttajat"], range= date + "!A1",
    valueInputOption="RAW", body=body).execute()

    return len(users)

def export_transactions():
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=settings.secrets["sheets"]["tapahtumat"], range="A1:F").execute()
    values = result.get('values', [])

    end = "2019-01-01"
    if len(values) > 1:
        end = values[-1][5]

    trans = db.get_transactions_after(end)

    mapped = list(map(lambda x: [str(i) for i in x], trans))

    body = {"values": mapped}

    result = service.spreadsheets().values().append(
        spreadsheetId=settings.secrets["sheets"]["tapahtumat"], range="A1:A",
        valueInputOption="RAW", body=body).execute()

    return len(trans)

def get_secrets(env):
    sheet_id = settings.settings["config_drive"]
    service = build('sheets', 'v4', credentials=creds)

    sheet = service.spreadsheets()

    admins = sheet.values().get(spreadsheetId=sheet_id, range="Admins!A1:Z").execute()["values"]

    admin_dict = {}
    for i in admins[1:]:
        admin_dict[i[0]] = {"sales_report": int(i[3]), "backup_report": int(i[4])}

    chats = sheet.values().get(spreadsheetId=sheet_id, range="Chats!A1:Z").execute()["values"]

    chat_dict = {}

    for i in chats[1:]:
        if i[1] == env:
            chat_dict[i[0].replace("−", "-")] = {"messages": int(i[2]), "daily_report": int(i[3]), "backup_report": int(i[4])}
    
    counter = 0
    for i in chat_dict:
        counter += chat_dict[i]["messages"]

    assert counter < 2, "Valitse Driven Config-sheetissä vain yksi chätti, johon viestejä välitetään tässä ympäristössä."

    bots = sheet.values().get(spreadsheetId=sheet_id, range="Bots!A1:Z").execute()["values"]
    for i in bots[1:]:
        if i[1] == env:
            bot_token = i[0]

    sheets_dict = {}
    sheets = sheet.values().get(spreadsheetId=sheet_id, range="Sheets!A1:Z").execute()["values"]
    for i in sheets[1:]:
        if i[1] == env:
            sheets_dict[i[2]] = i[0]

    secrets = {"admins": admin_dict, "chats": chat_dict, "bot_token": bot_token, "sheets": sheets_dict}

    return secrets


def main():
    import_inventory()
    export_transactions()

if __name__ == '__main__':
    main()
