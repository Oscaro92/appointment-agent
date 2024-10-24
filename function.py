import os, uuid
from pathlib import Path
from decouple import config
from datetime import datetime, timedelta
# * google
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

GMAIL_USER = config('GMAIL_USER')


def getBusy() -> list:
    try:
        print("IN getBusy")
        # auth
        BASE_DIR = Path(__file__).resolve().parent

        CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
        SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(GMAIL_USER)
        calendar = build('calendar', 'v3', credentials=delegated_credentials)

        body = {
            "timeMin": datetime.now().isoformat() + 'Z',
            "timeMax": (datetime.now() + timedelta(days=3)).isoformat() + 'Z',
            "items": [{"id": 'primary'}]
        }

        result = calendar.freebusy().query(body=body).execute()

        for r in result['calendars']['primary']['busy']:
            r['start'] = r['start'].replace('Z', '+02:00')
            r['end'] = r['end'].replace('Z', '+02:00')

        print(result)

        return result['calendars']['primary']['busy']
    except Exception as e:
        print(f"Error : {e}")
        return {}

def createRDV(data) -> str:
    try:
        print("IN createRDV")
        # auth
        BASE_DIR = Path(__file__).resolve().parent

        CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
        SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        delegated_credentials = credentials.with_subject(GMAIL_USER)
        calendar = build('calendar', 'v3', credentials=delegated_credentials)

        # config event
        event = {
            'summary': data['summary'],
            'start': {
                'dateTime': data['date_start'],
                'timeZone': 'Europe/Paris',
            },
            'end': {
                'dateTime': data['date_end'],
                'timeZone': 'Europe/Paris',
            },
            'description': f'Le numéro de téléphone de {data["full_name"]} est le : {data["phone"]}',
            'attendees': [
                {'email': data['email'], 'responseStatus': 'accepted'},
            ],
            'conferenceData': {
                'createRequest': {
                    'requestId': f'{str(uuid.uuid4())}',
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }

        # create event
        calendar.events().insert(calendarId='oscar@pigallestud.io', body=event, conferenceDataVersion=1, sendUpdates='all').execute()

        return "ok"
    except Exception as e:
        print(f"Error : {e}")
        return "error"
