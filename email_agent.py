# email_agent.py
import re
import requests

class EmailAgent:
    """
    Agent that processes raw email content, extracts fields,
    determines urgency, detects intent, and prepares structured CRM-like data.
    """

    def __init__(self, memory):
        self.memory = memory

    def extract_email_fields(self, email_text):
        # Normalize line endings and split into lines
        lines = email_text.replace('\r\n', '\n').split('\n')
        
        # Initialize with default values
        sender = "Unknown"
        subject = ""
        
        # Parse headers line by line
        for line in lines:
            # Stop processing headers at the first empty line
            if not line.strip():
                break
                
            # Extract sender (From:)
            if line.lower().startswith('from:'):
                sender = line[5:].strip()
                # Extract email from "Name <email@example.com>" format
                email_match = re.search(r'<([^>]+)>', sender)
                if email_match:
                    sender = email_match.group(1)
                # Remove any remaining angle brackets or quotes
                sender = re.sub(r'[<>"\']', '', sender).strip()
                
            # Extract subject
            elif line.lower().startswith('subject:'):
                subject = line[8:].strip()
                # Handle multi-line subjects if needed
                next_line = lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else ""
                while next_line and (next_line.startswith('\t') or next_line.startswith(' ')):
                    subject += ' ' + next_line.strip()
                    next_line = lines[lines.index(next_line) + 1] if lines.index(next_line) + 1 < len(lines) else ""
        
        # Clean up subject if it contains other headers
        subject = re.split(r'\s*(?:To:|Date:|From:).*$', subject, flags=re.IGNORECASE)[0].strip()
        
        # Urgency based on keywords in subject and first 500 chars of body
        body_start = email_text.find('\n\n')  # Find first empty line after headers
        body_sample = email_text[body_start:body_start+500] if body_start != -1 else email_text
        
        urgency_indicators = [
            'urgent', 'asap', 'immediately', 'important', 'attention',
            'time-sensitive', 'action required', 'response needed'
        ]
        
        urgency = "High" if any(
            re.search(rf'\b{re.escape(term)}\b', f"{subject} {body_sample}", re.IGNORECASE)
            for term in urgency_indicators
        ) else "Normal"

        return sender, subject, urgency

    def detect_intent_with_ollama(self, email_text):
        prompt = f"""
You are an intent classification model for emails.
Classify the user's intent from the following email text.

Available intents: reminder, meeting_request, task_update, follow_up, other

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
                if output in ["reminder", "meeting_request", "task_update", "follow_up", "other"]:
                    return output
            return "other"
        except Exception:
            return "other"

    def process_email(self, email_text, conversation_id=None):
        sender, subject, urgency = self.extract_email_fields(email_text)
        intent = self.detect_intent_with_ollama(email_text)

        crm_data = {
            "sender": sender,
            "subject": subject,
            "urgency": urgency,
            "original_text": email_text.strip(),
            "intent": intent
        }

        self.memory.log("Email", crm_data, conversation_id=conversation_id, sender=sender)
        return crm_data
