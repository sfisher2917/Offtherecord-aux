"""PayPal webhook validation helpers. No external HTTP endpoint is deployed by this module."""
from decimal import Decimal, InvalidOperation

ALLOWED_EVENT = "PAYMENT.CAPTURE.COMPLETED"
EXPECTED_AMOUNT = Decimal("75.00")

def validate_capture(event):
    if event.get("event_type") != ALLOWED_EVENT:
        return False, "unsupported event"
    resource = event.get("resource") or {}
    if resource.get("status") != "COMPLETED":
        return False, "capture not completed"
    amount = resource.get("amount") or {}
    if amount.get("currency_code") != "USD":
        return False, "wrong currency"
    try:
        value = Decimal(str(amount.get("value")))
    except (InvalidOperation, TypeError):
        return False, "invalid amount"
    if value != EXPECTED_AMOUNT:
        return False, "wrong amount"
    if not resource.get("id"):
        return False, "missing capture id"
    return True, resource["id"]

def verified_capture(event, signature_verified):
    if signature_verified is not True:
        return False, "unverified PayPal webhook signature"
    return validate_capture(event)
