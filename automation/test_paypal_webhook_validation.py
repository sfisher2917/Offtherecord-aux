import unittest
from paypal_webhook_validation import verified_capture

def event(amount="75.00",currency="USD",status="COMPLETED",kind="PAYMENT.CAPTURE.COMPLETED"):
    return {"event_type":kind,"resource":{"id":"sandbox-capture-001","status":status,"amount":{"value":amount,"currency_code":currency}}}

class TestWebhook(unittest.TestCase):
    def test_valid_verified_capture(self): self.assertEqual((True,"sandbox-capture-001"),verified_capture(event(),True))
    def test_reject_unverified(self): self.assertFalse(verified_capture(event(),False)[0])
    def test_reject_wrong_amount(self): self.assertFalse(verified_capture(event("35.00"),True)[0])
    def test_reject_wrong_currency(self): self.assertFalse(verified_capture(event(currency="EUR"),True)[0])
    def test_reject_pending(self): self.assertFalse(verified_capture(event(status="PENDING"),True)[0])
    def test_reject_other_event(self): self.assertFalse(verified_capture(event(kind="CHECKOUT.ORDER.APPROVED"),True)[0])
if __name__=="__main__": unittest.main()
