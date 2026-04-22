import hashlib
import hmac
from datetime import date
from fastapi import APIRouter, Request, Response, BackgroundTasks, HTTPException
import config
import messenger
import parser
import categorizer
import sheets
import commands

router = APIRouter()


def _verify_signature(body: bytes, signature_header: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = hmac.new(
        config.FB_PAGE_ACCESS_TOKEN.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header[7:])


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == config.FB_VERIFY_TOKEN
    ):
        return Response(content=params.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()
    sig = request.headers.get("X-Hub-Signature-256", "")
    if config.FB_PAGE_ACCESS_TOKEN and not _verify_signature(body, sig):
        raise HTTPException(status_code=403, detail="Bad signature")

    data = await request.json()
    background_tasks.add_task(_process_event, data)
    # Must return 200 immediately — Facebook retries if we take >20s
    return Response(content="EVENT_RECEIVED", status_code=200)


async def _process_event(data: dict):
    try:
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                psid = event.get("sender", {}).get("id", "")

                # Only respond to the owner
                if config.FB_USER_PSID and psid != config.FB_USER_PSID:
                    print(f"[webhook] Ignored message from unknown PSID: {psid}")
                    continue

                # Log PSID if not yet configured (first run)
                if not config.FB_USER_PSID:
                    print(f"[webhook] First message — your PSID is: {psid}")

                message = event.get("message", {})
                text = message.get("text", "").strip()
                if not text:
                    continue

                _handle_message(psid, text)
    except Exception as e:
        print(f"[webhook] Error processing event: {e}")


def _handle_message(psid: str, text: str):
    # Check for commands first
    if text.startswith("!"):
        reply = commands.handle_command(text)
        if reply:
            messenger.send_message(psid, reply)
        else:
            messenger.send_message(psid, "Unknown command. Type !help to see available commands.")
        return

    # Parse expense lines
    expenses = parser.parse_expenses(text)
    if not expenses:
        messenger.send_message(
            psid,
            "I didn't catch any expenses.\nFormat: ₱amount - item name\nExample: ₱440 - CYO Burger",
        )
        return

    today = date.today()
    confirmation_lines = []

    for expense in expenses:
        category = categorizer.categorize(expense["item"])
        sheets.append_expense(today, expense["amount"], expense["item"], category)
        amount_str = f"₱{expense['amount']:,.0f}"
        confirmation_lines.append(f"  {amount_str} - {expense['item']} → {category}")

    count = len(expenses)
    header = f"✅ Logged {count} expense{'s' if count > 1 else ''}:\n"
    messenger.send_message(psid, header + "\n".join(confirmation_lines))
