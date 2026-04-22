import httpx
import config

CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Health & Fitness",
    "Entertainment",
    "Travel",
    "Bills & Utilities",
    "Personal Care",
    "Other",
]

SYSTEM_PROMPT = (
    "You are a personal finance categorizer. Given an item name, return ONLY the category name "
    "— nothing else, no punctuation, no explanation.\n\n"
    "Categories (choose exactly one):\n"
    + "\n".join(f"- {c}" for c in CATEGORIES)
    + "\n\nIf unsure, return: Other"
)


def categorize(item: str) -> str:
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-haiku-4-5",
                "max_tokens": 20,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": item},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        category = response.json()["choices"][0]["message"]["content"].strip()
        if category not in CATEGORIES:
            return "Other"
        return category
    except Exception:
        return "Other"
