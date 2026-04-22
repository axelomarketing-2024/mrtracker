import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, datetime
from typing import List, Dict
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_NAME = "Expenses"
HEADERS = ["Date", "Time", "Day", "Amount", "Item", "Category", "Week Number", "Month"]

_client = None
_sheet = None


def _get_sheet():
    global _client, _sheet
    if _sheet is None:
        creds_dict = json.loads(config.GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _client = gspread.authorize(creds)
        spreadsheet = _client.open_by_key(config.GOOGLE_SHEET_ID)
        try:
            _sheet = spreadsheet.worksheet(SHEET_NAME)
        except gspread.WorksheetNotFound:
            _sheet = spreadsheet.add_worksheet(SHEET_NAME, rows=10000, cols=len(HEADERS))
            _sheet.append_row(HEADERS)
    return _sheet


def append_expense(expense_date: date, amount: float, item: str, category: str):
    now = datetime.now()
    iso = expense_date.isocalendar()
    row = [
        expense_date.strftime("%Y-%m-%d"),
        now.strftime("%H:%M"),
        expense_date.strftime("%A"),
        amount,
        item,
        category,
        iso.week,
        expense_date.strftime("%B"),
    ]
    _get_sheet().append_row(row, value_input_option="USER_ENTERED")


def get_expenses_for_date(target_date: date) -> List[Dict]:
    return get_expenses_for_date_range(target_date, target_date)


def get_expenses_for_date_range(start: date, end: date) -> List[Dict]:
    records = _get_sheet().get_all_records()
    results = []
    for r in records:
        try:
            row_date = datetime.strptime(r["Date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if start <= row_date <= end:
            results.append({
                "date": row_date,
                "time": r.get("Time", ""),
                "day": r.get("Day", ""),
                "amount": float(r.get("Amount", 0)),
                "item": r.get("Item", ""),
                "category": r.get("Category", "Other"),
            })
    return results
