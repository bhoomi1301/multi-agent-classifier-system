from classifier_agent import ClassifierAgent

agent = ClassifierAgent()

# Sample Email
email_input = """
From: john.doe@buyer.com
To: sales@steelco.com
Subject: Request for Quotation

Hi team,

I would like to request a quotation for 200 units of your steel rods.

Best regards,
John
"""
print("Email:", agent.classify(email_input, source_hint="Email"))
print()

# Sample JSON (Invoice)
json_input = """
{
  "invoice_id": "INV12345",
  "amount": 1520.75,
  "date": "2024-11-25",
  "vendor": "Tech Supplies Inc."
}
"""
print("JSON:", agent.classify(json_input, source_hint="JSON"))
print()

# Simulated PDF Text (Regulation)
pdf_input = """
Regulatory Notice

As per the updated compliance regulations by the Environmental Control Board, all industrial facilities must submit annual emission reports by December 1st, 2024.
"""
print("PDF:", agent.classify(pdf_input, source_hint="PDF"))
