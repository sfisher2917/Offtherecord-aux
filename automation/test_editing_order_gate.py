"""Dry-run validation for OffTheRecord.aux editing orders; no payments are made."""
import unittest
from dataclasses import dataclass

@dataclass
class Order:
    amount_cents: int
    currency: str
    payment_verified: bool
    source_received: bool
    footage_rights_confirmed: bool
    brief_received: bool
    videos_completed: int = 0
    revision_rounds: int = 0

def gate(order):
    errors=[]
    if order.amount_cents != 7500 or order.currency != "USD": errors.append("wrong payment amount/currency")
    if not order.payment_verified: errors.append("payment not independently verified")
    if not order.source_received: errors.append("customer footage missing")
    if not order.footage_rights_confirmed: errors.append("customer footage rights not confirmed")
    if not order.brief_received: errors.append("editing brief missing")
    return errors

def delivery_gate(order):
    errors=gate(order)
    if order.videos_completed != 3: errors.append("three finished videos required")
    if order.revision_rounds > 1: errors.append("revision scope exceeded")
    return errors

class OrderGateTests(unittest.TestCase):
    def test_unpaid_is_blocked(self):
        self.assertIn("payment not independently verified",gate(Order(7500,"USD",False,True,True,True)))
    def test_missing_rights_is_blocked(self):
        self.assertIn("customer footage rights not confirmed",gate(Order(7500,"USD",True,True,False,True)))
    def test_wrong_amount_is_blocked(self):
        self.assertTrue(gate(Order(3500,"USD",True,True,True,True)))
    def test_paid_complete_intake_passes(self):
        self.assertEqual([],gate(Order(7500,"USD",True,True,True,True)))
    def test_delivery_requires_three(self):
        self.assertIn("three finished videos required",delivery_gate(Order(7500,"USD",True,True,True,True,2)))
    def test_complete_delivery_passes(self):
        self.assertEqual([],delivery_gate(Order(7500,"USD",True,True,True,True,3)))
if __name__=="__main__": unittest.main()
