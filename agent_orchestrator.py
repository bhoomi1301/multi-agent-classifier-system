import json
from memory_store import MemoryStore
from classifier_agent import ClassifierAgent
from email_agent import EmailAgent
from json_agent import JSONAgent
from pdf_agent import PDFAgent

from rfq_agent import process_rfq
from complaint_agent import process_complaint
from regulation_agent import process_regulation
from other_agent import process_other

class AgentOrchestrator:
    def __init__(self):
        self.memory = MemoryStore()
        self.classifier = ClassifierAgent()
        self.email_agent = EmailAgent(self.memory)
        self.json_agent = JSONAgent(self.memory)
        self.pdf_agent = PDFAgent(self.memory)

    def route_input(self, input_data, conversation_id=None, sender=None, input_format=None, source_hint=None):
        hint = source_hint or input_format or (input_data if isinstance(input_data, str) and len(input_data) < 1000 else None)
        classification = self.classifier.classify(input_data, source_hint=hint or "Unknown")
        format_type = input_format or classification.get("format", "Unknown")
        intent = classification.get("intent", "Other").lower()

        print(f"[Classifier] Detected format: {format_type}, intent: {intent}")

        if format_type == "Email":
            email_data = self.email_agent.process_email(input_data)
            email_data["intent"] = intent
            result = self._route_by_intent(email_data)
            self.memory.add_entry("Email", {"classification": classification, "result": result}, sender=sender, conversation_id=conversation_id)
            return result

        elif format_type == "JSON":
            try:
                if isinstance(input_data, dict):
                    json_data = input_data
                else:
                    json_data = json.loads(input_data)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON input"}
            json_data["intent"] = intent
            result = self._route_by_intent(json_data)
            self.memory.add_entry("JSON", {"classification": classification, "result": result}, sender=sender, conversation_id=conversation_id)
            return result

        elif format_type == "PDF":
            text = self.pdf_agent.extract_text_from_pdf(input_data)
            if text.startswith("[ERROR]"):
                return {"error": text}
            
            # Process the PDF with the extracted text
            result = self.pdf_agent.process_pdf(text, classification)
            
            # Route based on intent
            if isinstance(result, dict) and 'intent' in result:
                result = self._route_by_intent(result)
            
            # Log to memory
            self.memory.add_entry(
                "PDF",
                {"classification": classification, "result": result},
                sender=sender,
                conversation_id=conversation_id
            )
            return result

        else:
            return {"error": "Unsupported format"}

    def _route_by_intent(self, payload):
        intent = payload.get("intent", "other").lower()

        if intent == "invoice":
            return self.json_agent.process_json(payload)
        elif intent == "rfq":
            return process_rfq(payload, self.memory)
        elif intent == "complaint":
            return process_complaint(payload, self.memory)
        elif intent == "regulation":
            return process_regulation(payload, self.memory)
        else:
            return process_other(payload, self.memory)

    def get_memory(self):
        return self.memory.get_all()
