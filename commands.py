from datetime import date, timedelta
from typing import Optional
import sheets
import reports

HELP_TEXT = """Finance Tracker Commands:

!today / !eod   — Today's expenses
!week  / !eow   — This week's expenses
!month / !eom   — This month's expenses
!help           — Show this menu

To log expenses, just send:
₱440 - CYO Burger
₱50 - Parking"""


def handle_command(text: str) -> Optional[str]:
    cmd = text.strip().lower()

    if cmd in ("!help",):
        return HELP_TEXT

    if cmd in ("!today", "!eod"):
        today = date.today()
        expenses = sheets.get_expenses_for_date(today)
        return reports.build_eod_report(today, expenses)

    if cmd in ("!week", "!eow"):
        today = date.today()
        # Current week Mon–today
        start = today - timedelta(days=today.weekday())
        expenses = sheets.get_expenses_for_date_range(start, today)
        return reports.build_eow_report(start, today, expenses)

    if cmd in ("!month", "!eom"):
        today = date.today()
        start = today.replace(day=1)
        expenses = sheets.get_expenses_for_date_range(start, today)
        return reports.build_eom_report(today.year, today.month, expenses)

    return None
