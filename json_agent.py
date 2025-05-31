# json_agent.py

import requests

class JSONAgent:
    """
    Agent that processes structured JSON payloads (e.g., invoices, RFQs, complaints),
    validates fields based on intent, and logs results with anomalies.
    """

    def __init__(self, memory):
        self.memory = memory

        self.required_fields_by_intent = {
            "invoice": ["invoice_id", "vendor", "amount", "date"],
            "rfq": ["rfq_id", "client_name", "product", "quantity", "deadline"],
            "complaint": ["ticket_id", "customer_name", "issue", "reported_date"],
        }

    def detect_intent_with_ollama(self, email_text):
        prompt = f"""
You are an intent classification model for emails.
Classify the user's intent from the following email text.

Available intents: invoice, rfq, complaint, other

Email:
\"\"\"
{email_text}
\"\"\"

Reply with only the intent label from the list above.
"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=10
            )
            if response.status_code == 200:
                output = response.json().get("response", "").strip().lower()
                if output in ["invoice", "rfq", "complaint", "other"]:
                    return output
            return "other"
        except Exception:
            return "other"

    def process_json(self, json_data, conversation_id=None, sender=None):
        missing_fields = []
        anomalies = []

        intent = json_data.get("intent", "").lower()
        # If intent empty or unknown, try detecting intent using raw_text field
        if not intent or intent not in self.required_fields_by_intent:
            raw_text = json_data.get("raw_text", "")
            if raw_text:
                intent = self.detect_intent_with_ollama(raw_text)
            else:
                intent = "other"

        required_fields = self.required_fields_by_intent.get(intent, [])

        if not required_fields and intent != "other":
            anomalies.append(f"Unknown or unsupported intent: {intent}")

        for field in required_fields:
            if field not in json_data or json_data[field] in [None, ""]:
                missing_fields.append(field)

        if intent == "invoice":
            amount = json_data.get("amount")
            if amount is not None:
                if not isinstance(amount, (int, float)):
                    anomalies.append("Amount not numeric")
                elif amount <= 0:
                    anomalies.append("Amount not positive")
            else:
                anomalies.append("Amount missing")

        elif intent == "rfq":
            quantity = json_data.get("quantity")
            if quantity is not None:
                if not isinstance(quantity, int):
                    anomalies.append("Quantity not an integer")
                elif quantity <= 0:
                    anomalies.append("Quantity not positive")
            else:
                anomalies.append("Quantity missing")

        elif intent == "complaint":
            issue = json_data.get("issue", "")
            if isinstance(issue, str) and len(issue.strip()) < 10:
                anomalies.append("Issue description too short")

        json_data["intent"] = intent
        json_data["missing_fields"] = missing_fields
        json_data["anomalies"] = anomalies

        self.memory.log("JSON", json_data, conversation_id=conversation_id, sender=sender)

        return json_data
