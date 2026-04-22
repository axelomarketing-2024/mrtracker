import httpx
import config

GRAPH_URL = "https://graph.facebook.com/v21.0/me/messages"


def send_message(psid: str, text: str) -> bool:
    payload = {
        "recipient": {"id": psid},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    params = {"access_token": config.FB_PAGE_ACCESS_TOKEN}
    try:
        response = httpx.post(GRAPH_URL, json=payload, params=params, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[messenger] Failed to send message: {e}")
        return False
