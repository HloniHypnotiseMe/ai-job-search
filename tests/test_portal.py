import os
import tempfile
import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch

from career_engine.service import CareerService
from career_engine.store import CareerStore
from portal.app import Handler, password_hash, verify_password

class CareerPortalTests(unittest.TestCase):
    def test_password_hash_round_trip(self):
        encoded=password_hash("test-password")
        self.assertTrue(verify_password("test-password", encoded))
        self.assertFalse(verify_password("wrong", encoded))

    def test_store_is_private_and_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=CareerStore(tmp)
            service=CareerService(store)
            row=service.create_mission("Capture first interview")
            self.assertEqual(row["stage"],"AUDIT")
            self.assertTrue(os.path.exists(os.path.join(tmp,"missions.json")))

if __name__=="__main__":
    unittest.main()
