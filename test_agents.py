import unittest
from unittest.mock import MagicMock
from json_agent import JSONAgent
from email_agent import EmailAgent

class TestJSONAgent(unittest.TestCase):
    def setUp(self):
        # Mock memory with a simple log method
        self.mock_memory = MagicMock()
        self.agent = JSONAgent(self.mock_memory)

    def test_invoice_valid(self):
        data = {
            "intent": "invoice",
            "invoice_id": "INV123",
            "vendor": "Vendor A",
            "amount": 1500.50,
            "date": "2025-05-31"
        }
        result = self.agent.process_json(data)
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(result["anomalies"], [])
        self.mock_memory.log.assert_called_once_with("JSON", result)

    def test_invoice_missing_fields_and_anomalies(self):
        data = {
            "intent": "invoice",
            "invoice_id": "",
            "vendor": None,
            "amount": -50,
            "date": ""
        }
        result = self.agent.process_json(data)
        self.assertIn("invoice_id", result["missing_fields"])
        self.assertIn("vendor", result["missing_fields"])
        self.assertIn("date", result["missing_fields"])
        self.assertIn("Amount not positive", result["anomalies"])

    def test_unknown_intent(self):
        data = {"intent": "unknown_intent"}
        result = self.agent.process_json(data)
        self.assertIn("Unknown or unsupported intent: unknown_intent", result["anomalies"])

    def test_complaint_short_issue(self):
        data = {
            "intent": "complaint",
            "ticket_id": "T123",
            "customer_name": "John Doe",
            "issue": "Too bad",
            "reported_date": "2025-05-30"
        }
        result = self.agent.process_json(data)
        self.assertIn("Issue description too short", result["anomalies"])


class TestEmailAgent(unittest.TestCase):
    def setUp(self):
        self.mock_memory = MagicMock()
        self.agent = EmailAgent(self.mock_memory)

    def test_extract_email_fields(self):
        email_text = (
            "From: alice@example.com\n"
            "Subject: Urgent: Please respond ASAP\n"
            "Body: This is an urgent request."
        )
        sender, subject, urgency = self.agent.extract_email_fields(email_text)
        self.assertEqual(sender, "alice@example.com")
        self.assertEqual(subject, "Urgent: Please respond ASAP")
        self.assertEqual(urgency, "High")

    def test_process_email_normal_urgency(self):
        email_text = (
            "From: bob@example.com\n"
            "Subject: Meeting notes\n"
            "Body: Here are the meeting notes."
        )
        result = self.agent.process_email(email_text)
        self.assertEqual(result["sender"], "bob@example.com")
        self.assertEqual(result["subject"], "Meeting notes")
        self.assertEqual(result["urgency"], "Normal")
        self.mock_memory.log.assert_called_once_with("Email", result)

    def test_extract_email_fields_missing_sender_subject(self):
        email_text = "Body: No header info"
        sender, subject, urgency = self.agent.extract_email_fields(email_text)
        self.assertEqual(sender, "Unknown")
        self.assertEqual(subject, "")
        self.assertEqual(urgency, "Normal")


if __name__ == "__main__":
    unittest.main()
