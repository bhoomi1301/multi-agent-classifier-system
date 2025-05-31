from classifier_agent import ClassifierAgent
from json_agent import JSONAgent
from email_agent import EmailAgent
from pdf_agent import PDFAgent
from rfq_agent import process_rfq
from complaint_agent import process_complaint
from regulation_agent import process_regulation
from other_agent import process_other
from shared_memory import SharedMemory

memory = SharedMemory()
json_agent = JSONAgent(memory)
email_agent = EmailAgent(memory)
classifier = ClassifierAgent()
pdf_agent = PDFAgent(memory)

def orchestrate(input_data, input_type):
    if input_type.lower() == "pdf":
        return pdf_agent.process_pdf(input_data)

    elif input_type.lower() == "json":
        if isinstance(input_data, str):
            import json
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON input."}

        classification = classifier.classify(str(input_data), source_hint="JSON")
        intent = classification.get("intent", "Other")

        if intent == "Invoice":
            return json_agent.process_json(input_data)
        elif intent == "RFQ":
            return process_rfq(input_data, memory)
        elif intent == "Complaint":
            return process_complaint(input_data, memory)
        elif intent == "Regulation":
            return process_regulation(input_data, memory)
        else:
            return process_other(input_data, memory)

    elif input_type.lower() == "email":
        classification = classifier.classify(input_data, source_hint="Email")
        intent = classification.get("intent", "Other")

        email_info = email_agent.process_email(input_data)

        if intent == "Invoice":
            return json_agent.process_json(email_info)
        elif intent == "RFQ":
            return process_rfq(email_info, memory)
        elif intent == "Complaint":
            return process_complaint(email_info, memory)
        elif intent == "Regulation":
            return process_regulation(email_info, memory)
        else:
            return process_other(email_info, memory)

    else:
        return {"error": "Unknown input type"}
