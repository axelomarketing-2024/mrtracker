from datetime import date, timedelta
from typing import List, Dict
from collections import defaultdict
import calendar

CATEGORY_EMOJI = {
    "Food & Dining": "🍽",
    "Transport": "🚗",
    "Shopping": "🛍",
    "Health & Fitness": "💪",
    "Entertainment": "🎬",
    "Travel": "✈️",
    "Bills & Utilities": "💡",
    "Personal Care": "🪥",
    "Other": "📦",
}


def _fmt(amount: float) -> str:
    return f"₱{amount:,.0f}"


def _group_by_category(expenses: List[Dict]) -> Dict[str, List[Dict]]:
    groups = defaultdict(list)
    for e in expenses:
        groups[e["category"]].append(e)
    return groups


def build_eod_report(target_date: date, expenses: List[Dict]) -> str:
    if not expenses:
        return f"📊 End of Day — {target_date.strftime('%A, %B %-d')}\n\nNo expenses logged today."

    total = sum(e["amount"] for e in expenses)
    groups = _group_by_category(expenses)

    lines = [
        f"📊 End of Day — {target_date.strftime('%A, %B %-d, %Y')}",
        "",
        f"Total Spent: {_fmt(total)}",
        "",
    ]

    for category, items in sorted(groups.items(), key=lambda x: -sum(i["amount"] for i in x[1])):
        cat_total = sum(i["amount"] for i in items)
        emoji = CATEGORY_EMOJI.get(category, "📦")
        lines.append(f"{emoji} {category} ({_fmt(cat_total)})")
        for item in items:
            lines.append(f"   • {item['item']} — {_fmt(item['amount'])}")
        lines.append("")

    return "\n".join(lines).rstrip()


def build_eow_report(start: date, end: date, expenses: List[Dict]) -> str:
    label = f"{start.strftime('%B %-d')}–{end.strftime('%-d, %Y')}"

    if not expenses:
        return f"📊 Week of {label}\n\nNo expenses logged this week."

    total = sum(e["amount"] for e in expenses)
    groups = _group_by_category(expenses)

    lines = [
        f"📊 Week of {label}",
        "",
        f"Total Spent: {_fmt(total)}",
        "",
        "Category Breakdown:",
    ]

    for category, items in sorted(groups.items(), key=lambda x: -sum(i["amount"] for i in x[1])):
        cat_total = sum(i["amount"] for i in items)
        pct = round(cat_total / total * 100)
        emoji = CATEGORY_EMOJI.get(category, "📦")
        lines.append(f"  {emoji} {category} — {_fmt(cat_total)} ({pct}%)")

    # Daily totals
    lines.append("")
    lines.append("Daily:")
    daily = defaultdict(float)
    for e in expenses:
        daily[e["date"]] += e["amount"]

    day_parts = []
    current = start
    while current <= end:
        spent = daily.get(current, 0.0)
        day_parts.append(f"{current.strftime('%a')} {_fmt(spent)}")
        current += timedelta(days=1)
    lines.append("  " + " · ".join(day_parts))

    return "\n".join(lines)


def build_eom_report(year: int, month: int, expenses: List[Dict]) -> str:
    month_name = calendar.month_name[month]
    label = f"{month_name} {year}"
    days_in_month = calendar.monthrange(year, month)[1]

    if not expenses:
        return f"📊 {label} — Monthly Report\n\nNo expenses logged this month."

    total = sum(e["amount"] for e in expenses)
    daily_avg = total / days_in_month
    groups = _group_by_category(expenses)

    lines = [
        f"📊 {label} — Monthly Report",
        "",
        f"Total Spent: {_fmt(total)}",
        f"Daily Average: {_fmt(daily_avg)}",
        "",
        "Category Breakdown:",
    ]

    for category, items in sorted(groups.items(), key=lambda x: -sum(i["amount"] for i in x[1])):
        cat_total = sum(i["amount"] for i in items)
        pct = round(cat_total / total * 100)
        emoji = CATEGORY_EMOJI.get(category, "📦")
        lines.append(f"  {emoji} {category} — {_fmt(cat_total)} ({pct}%)")

    # Top 5 single expenses
    top5 = sorted(expenses, key=lambda x: -x["amount"])[:5]
    lines.append("")
    lines.append("Top 5 Expenses:")
    for i, e in enumerate(top5, 1):
        lines.append(f"  {i}. {e['item']} — {_fmt(e['amount'])}")

    return "\n".join(lines)
