"""
This file provides authorization to Google services.
Used by fkcal and db.drive modules.
"""

import os
from google.oauth2.service_account import Credentials

creds = Credentials.from_service_account_file(
    os.environ.get("GOOGLE_SERVICE_ACCOUNT_CREDS", "google_service_account_creds.json"),
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/calendar.readonly",
    ],
)
