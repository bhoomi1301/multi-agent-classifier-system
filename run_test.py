from agent_orchestrator import AgentOrchestrator
import json

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Sample Email Input
email_input = """
From: John Doe <john@example.com>
Subject: RFQ for laptops

Hi Team,

We need a quotation for 25 laptops with high-end specs. Please send ASAP.

Thanks,
John
"""

# Sample JSON Input
json_input = json.dumps({
    "invoice_id": "INV-001",
    "vendor": "Dell",
    "amount": 0,  # Will flag anomaly
    "date": "2025-05-31"
})

# Test Email
print("\n--- Processing Email Input ---")
response_email = orchestrator.route_input(email_input)
print("Response:", response_email)

# Test JSON
print("\n--- Processing JSON Input ---")
response_json = orchestrator.route_input(json_input)
print("Response:", response_json)

# View shared memory
print("\n--- Memory Store ---")
print(orchestrator.get_memory())
