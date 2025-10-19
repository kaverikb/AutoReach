# apis/sheets_integration.py
import os
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = os.getenv("SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1  # assuming first sheet

def log_feedback(row: list):
    """Append a row of feedback to the sheet"""
    sheet.append_row(row)
