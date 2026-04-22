import re
from typing import List, Dict

# Matches: ₱440 - Item name  or  ₱1,600 – Item name  (hyphen or en-dash)
EXPENSE_PATTERN = re.compile(
    r"₱([\d,]+(?:\.\d+)?)\s*[-–]\s*(.+)"
)


def parse_expenses(text: str) -> List[Dict]:
    expenses = []
    # Normalize encoded newlines
    text = text.replace("\\n", "\n")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = EXPENSE_PATTERN.match(line)
        if match:
            amount_str = match.group(1).replace(",", "")
            item = match.group(2).strip()
            expenses.append({"amount": float(amount_str), "item": item})
    return expenses
