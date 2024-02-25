import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os

# Load JSON data
with open('timer_data.json') as json_file:
    data = json.load(json_file)

# Set up credentials
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'google.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Build Google Sheets API service
service = build('sheets', 'v4', credentials=creds)

# Spreadsheet ID and range
spreadsheet_id = '1k1fGqeaedVbdu6imcU8vFrKMJlXVTgZdZ8cHprv7SCk'
range_name = 'Sheet1'

# Flatten the JSON data to a list of rows
rows = []
for app_name, app_data in data.items():
    for tab_url, tab_info in app_data.get('tabs', {}).items():
        start_time = tab_info.get('start_time', '')
        end_time = tab_info.get('end_time', '')
        elapsed_time = f"{tab_info.get('elapsed_time_hours', 0):02}:{tab_info.get('elapsed_time_minutes', 0):02}:{tab_info.get('elapsed_time_seconds', 0):02}"
        active_tab_url = tab_info.get('active_tab_url', 'N/A')

        rows.append([app_name, tab_url, start_time, end_time, elapsed_time, active_tab_url])

# Prepare the values for updating the sheet
body = {
    'values': [['Application', 'Tab URL', 'Start Time', 'End Time', 'Elapsed Time (HH:MM:SS)', 'Active Tab URL']] + rows
}

# Update values in the sheet
result = service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id, range=range_name,
    valueInputOption='RAW', body=body).execute()

print('{0} cells updated in Google Sheet.'.format(result.get('updatedCells')))
