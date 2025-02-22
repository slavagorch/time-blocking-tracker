import os
import datetime
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

# Define local paths for credentials and token
LOCAL_CREDENTIALS_PATH = os.path.expanduser("~/.config/gcal_auth/credentials.json")
LOCAL_TOKEN_PATH = os.path.expanduser("~/.config/gcal_auth/token.json")

# Default to local credentials
CREDENTIALS_PATH = LOCAL_CREDENTIALS_PATH
TOKEN_PATH = LOCAL_TOKEN_PATH

# Check if an environment variable is set and points to a valid file
env_creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
if env_creds_path and os.path.exists(env_creds_path):
    CREDENTIALS_PATH = env_creds_path
    TOKEN_PATH = os.path.join(os.path.dirname(env_creds_path), "token.json")
else:
    # Attempt to load credentials from Streamlit secrets
    secrets = getattr(st, "secrets", None)
    if secrets and "google" in secrets and secrets["google"].get("credentials"):
        creds_json = secrets["google"]["credentials"].strip()
        if creds_json:
            # Write credentials to a temporary file on Streamlit Cloud
            CREDENTIALS_PATH = "/tmp/credentials.json"
            TOKEN_PATH = "/tmp/token.json"
            with open(CREDENTIALS_PATH, "w") as f:
                f.write(creds_json)

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate_google_calendar():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=8080)  # Force fixed port 8080

        # Save the new token in the same global config directory
        os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return creds

def get_all_calendar_events():
    creds = authenticate_google_calendar()
    service = build("calendar", "v3", credentials=creds) # Creates a API object with provided credentials

    # List all calendars
    calendars = service.calendarList().list().execute()

    today_start = datetime.datetime.now(datetime.UTC).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    calendar_events_dict = {}
    calendar_id_mapping = {}

    for cal in calendars.get("items", []):
        calendar_id = cal["id"]
        calendar_name = cal["summary"]  # Get calendar name
        calendar_color = cal.get("backgroundColor", "#000000")
        calendar_id_mapping[calendar_id] = {"name": calendar_name, "color": calendar_color}

        request = service.events().list(
            calendarId=calendar_id,
            timeMax=today_start,
            singleEvents=True,  # unpacks recurring events into individual instances
            timeZone="UTC",
            orderBy="startTime",
        )

        events = []
        # This loop handles pagination by iteratively fetching all pages of events.
        while request is not None:
            response = request.execute()
            events.extend(response.get("items", []))
            request = service.events().list_next(request, response)

        # Store events in dictionary
        calendar_events_dict[calendar_id] = {
            "name": calendar_name,
            "events": [
                {
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date"))
                }
                for event in events
            ]
        }

    return calendar_events_dict, calendar_id_mapping
