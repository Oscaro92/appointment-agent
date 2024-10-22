import os, uuid
from pathlib import Path
from datetime import datetime, timedelta
# * google
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


def getBusy() -> dict:
    # auth
    BASE_DIR = Path(__file__).resolve().parent

    CREDENTIALS_FILE = os.path.join(BASE_DIR, 'token.json')
    SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject('oscar@pigallestud.io')
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

    return result['calendars']['primary']['busy']

def createRDV(data: dict) -> str:
    try:
        # auth
        BASE_DIR = Path(__file__).resolve().parent

        CREDENTIALS_FILE = os.path.join(BASE_DIR, 'token.json')
        SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events']

        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        delegated_credentials = credentials.with_subject('oscar@pigallestud.io')
        calendar = build('calendar', 'v3', credentials=delegated_credentials)

        # config event
        event = {
            'summary': data['summary'],
            'start': {
                'dateTime': data['start'],
                'timeZone': 'Europe/Paris',
            },
            'end': {
                'dateTime': data['end'],
                'timeZone': 'Europe/Paris',
            },
            'description': f'Le numéro de téléphone de {data["name"]} est le : {data["phone"]}',
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
    except:
        return "error"
