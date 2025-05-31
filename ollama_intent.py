# ollama_intent.py
import requests

def detect_intent_with_ollama(email_text):
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

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        output = response.json()["response"].strip().lower()
        return output if output in ["reminder", "meeting_request", "task_update", "follow_up", "other"] else "other"
    else:
        return "other"
