# Time-Blocking Tracking

A tool that extracts past Google Calendar events, then displays a Streamlit dashboard for analyzing time-blocked habits.

## Features
* Google Calendar Integration: Authenticates via OAuth.
* Automated Data Extraction: Collects events from all your calendars (before today).
* Visual Dashboard: Bar charts showing total hours per week/month.

## Requirements
* Python 3.7+
* Google API Python Client

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

* Streamlit & Plotly

```
pip install streamlit plotly
```

* Pandas

```
pip install pandas
```

## Setting Up Google Calendar API Credentials & Authentication

To use this application, you need to authenticate with **Google Calendar API** using OAuth 2.0. Follow these steps carefully.

---

### **Step 1: Create a Google Cloud Project**
1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Sign in with your Google account.
3. Click on **"Select a project"** (top-left) → **"New Project"**.
4. Give your project a name (e.g., `Time-Blocking Tracker`) and click **"Create"**.

---

### **Step 2: Enable Google Calendar API**
1. Open the [Google API Library](https://console.cloud.google.com/apis/library).
2. Search for **Google Calendar API**.
3. Click **"Enable"**.

---

### **Step 3: Create OAuth 2.0 Credentials**
1. Navigate to **APIs & Services** → **Credentials**.
2. Click **"Create Credentials"** → **"OAuth client ID"**.
3. **Set up the OAuth consent screen** (if prompted):
   - Select **"External"** and click **"Create"**.
   - Fill in **App Name** (e.g., `Time-Blocking Tracker`).
   - Choose your **email** as the user support email.
   - Add **your email** under "Developer Contact Information".
   - Click **Save & Continue** until you reach the end, then click **"Back to Dashboard"**.

4. **Create OAuth Client ID**:
   - Application Type: **Web Application**.
   - Name: `Time-Blocking Tracker OAuth`.
   - Under **"Authorized redirect URIs"**, click **"Add URI"**.
     - Enter:  
       ```
       http://localhost:8080/
       ```
   - Click **"Create"**.

5. **Download credentials**:
   - After creation, a popup will show **client ID and secret**.
   - Click **"Download JSON"** to get `credentials.json`.

---

### **Step 4: Store Credentials Securely**
1. Move the downloaded `credentials.json` to the following location:
   - **Linux/macOS**:  
     ```bash
     mv ~/Downloads/credentials.json ~/.config/gcal_auth/credentials.json
     ```
   - **Windows (PowerShell)**:  
     ```powershell
     Move-Item -Path "$env:USERPROFILE\Downloads\credentials.json" -Destination "$env:APPDATA\gcal_auth\credentials.json"
     ```
2. (Optional) Set an environment variable:
   ```bash
   export GOOGLE_CREDENTIALS_PATH="$HOME/.config/gcal_auth/credentials.json"
   
## Usage
1. Run the Streamlit App

```
streamlit run app.py
```

2. Select a Calendar
   * Choose from the dropdown in your browser.
3. Choose Granularity
   * Week or Month.
4. View Total Time
   * Bar chart of hours per period.

## File Overview
* extract_data.py
   * Authenticates with Google Calendar.
   * Fetches past events (paginates all pages).
   * Returns dictionaries for calendar events and metadata.
* app.py
   * Streamlit UI for calendar selection, data resampling (Weekly/Monthly), and charting with Plotly.
   * Caches data to reduce API calls.

## Stay Connected 🚀

Consider subscribing to my **[Medium](https://medium.com/@slavagorch)** where I share insights on data science and automation.

You can also connect with me on **[LinkedIn](https://www.linkedin.com/in/slavagorch/)** to discuss projects, collaborations, or just to say hi!

Happy tracking! 🎯