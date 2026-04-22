from datetime import date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import config
import sheets
import reports
import messenger

MANILA = pytz.timezone("Asia/Manila")

scheduler = BackgroundScheduler(timezone=MANILA)


def _send_eod():
    today = date.today()
    expenses = sheets.get_expenses_for_date(today)
    report = reports.build_eod_report(today, expenses)
    if config.FB_USER_PSID:
        messenger.send_message(config.FB_USER_PSID, report)
    else:
        print("[scheduler] FB_USER_PSID not set — skipping EOD send")


def _send_eow():
    # Previous week: Mon to Sun
    today = date.today()
    end = today - timedelta(days=today.weekday() + 1)  # last Sunday
    start = end - timedelta(days=6)                     # last Monday
    expenses = sheets.get_expenses_for_date_range(start, end)
    report = reports.build_eow_report(start, end, expenses)
    if config.FB_USER_PSID:
        messenger.send_message(config.FB_USER_PSID, report)
    else:
        print("[scheduler] FB_USER_PSID not set — skipping EOW send")


def _send_eom():
    # Previous month
    today = date.today()
    last_day_prev = today.replace(day=1) - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    expenses = sheets.get_expenses_for_date_range(first_day_prev, last_day_prev)
    report = reports.build_eom_report(last_day_prev.year, last_day_prev.month, expenses)
    if config.FB_USER_PSID:
        messenger.send_message(config.FB_USER_PSID, report)
    else:
        print("[scheduler] FB_USER_PSID not set — skipping EOM send")


def start():
    # EOD: every day at 22:00 Manila time
    scheduler.add_job(_send_eod, CronTrigger(hour=22, minute=0, timezone=MANILA), id="eod")
    # EOW: every Monday at 08:00 Manila time
    scheduler.add_job(_send_eow, CronTrigger(day_of_week="mon", hour=8, minute=0, timezone=MANILA), id="eow")
    # EOM: 1st of every month at 08:00 Manila time
    scheduler.add_job(_send_eom, CronTrigger(day=1, hour=8, minute=0, timezone=MANILA), id="eom")
    scheduler.start()
    print("[scheduler] Started — EOD@22:00, EOW Mon@08:00, EOM 1st@08:00 (Asia/Manila)")


def stop():
    scheduler.shutdown(wait=False)
