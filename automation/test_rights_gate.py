import datetime as dt
import unittest
from automation.rights_gate import validate

class RightsGateTests(unittest.TestCase):
    def test_unverified_is_blocked(self):
        item={"id":"x","status":"ready","source_url":"https://example.org/a.mp4","platforms":["youtube"]}
        self.assertTrue(validate(item,"youtube"))
    def test_documented_rights_pass(self):
        item={"id":"x","status":"ready","source_url":"https://example.org/a.mp4","platforms":["youtube"],
              "rights":{"verification":"documented","licensor":"Example Rights Holder","license_id":"test-license",
              "evidence_url":"https://example.org/license","commercial_use":True,"editing":True,
              "audio":True,"video":True,"redistribution":True,"platforms":["youtube"],
              "expires_on":"2099-12-31"}}
        self.assertEqual(validate(item,"youtube",dt.date(2026,11,8)),[])
        item["rights"]["audio"]=False
        self.assertIn("both audio and video rights required",validate(item,"youtube"))
    def test_expiry_and_platform(self):
        item={"status":"ready","source_url":"https://example.org/a.mp4","platforms":["youtube"],
              "rights":{"verification":"documented","licensor":"Example","license_id":"test",
              "evidence_url":"https://example.org/license","commercial_use":True,"editing":True,
              "audio":True,"video":True,"redistribution":True,"platforms":["youtube"],
              "expires_on":"2025-01-01"}}
        self.assertIn("license expired",validate(item,"youtube",dt.date(2026,11,8)))
        self.assertIn("platform not approved for this item",validate(item,"instagram"))
if __name__=="__main__":unittest.main()
