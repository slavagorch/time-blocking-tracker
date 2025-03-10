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

# Check if running on Streamlit Cloud (secrets should exist)
if "google" in getattr(st, "secrets", {}):  # Ensures it doesn’t crash locally
    creds_json = st.secrets["google"].get("credentials", "").strip()

    if creds_json:
        # Override paths for Streamlit Cloud
        CREDENTIALS_PATH = "/tmp/credentials.json"
        TOKEN_PATH = "/tmp/token.json"

        # Save credentials to a temporary file
        with open(CREDENTIALS_PATH, "w") as f:
            f.write(creds_json)

# Ensure credentials file exists before proceeding
if not os.path.exists(CREDENTIALS_PATH):
    raise FileNotFoundError(
        f"Google API credentials not found. Expected at: {CREDENTIALS_PATH}. "
        "Ensure you have added credentials in Streamlit secrets or locally."
    )

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

            if os.getenv("STREAMLIT_SERVER"):  # Check if running in Streamlit Cloud
                creds = flow.run_console()  # Uses console authentication instead
            else:
                creds = flow.run_local_server(port=8080)  # Works locally

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
