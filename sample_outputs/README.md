# Sample Outputs

This directory contains example outputs for different types of document processing.

## 1. Emergency Issue Email Processing

File: `emergency_email_processing.log`
```
=== Processing Emergency Issue Email ===
[Classifier] Detected format: Email, intent: Support
[Email Agent] Sender: jane.doe@example.com
[Email Agent] Subject: [URGENT] Production System Down - Immediate Action Required
[Email Agent] Urgency: High
[Memory Log] Added entry with ID: abc123-456-789

=== Processing Result ===
{
  "status": "success",
  "classification": {
    "format": "Email",
    "intent": "Support"
  },
  "sender": "jane.doe@example.com",
  "subject": "[URGENT] Production System Down - Immediate Action Required",
  "urgency": "High",
  "summary": "Reported production system outage affecting all users. Immediate attention required.",
  "next_steps": [
    "Alert on-call engineer",
    "Initiate incident response",
    "Notify customer support team"
  ]
}
```

## 2. General Inquiry Email

File: `inquiry_email_processing.log`
```
=== Processing General Inquiry Email ===
[Classifier] Detected format: Email, intent: Inquiry
[Email Agent] Sender: alex.johnson@example.com
[Email Agent] Subject: Product Information Request
[Email Agent] Urgency: Normal
[Memory Log] Added entry with ID: def456-789-012

=== Processing Result ===
{
  "status": "success",
  "classification": {
    "format": "Email",
    "intent": "Inquiry"
  },
  "sender": "alex.johnson@example.com",
  "subject": "Product Information Request",
  "urgency": "Normal",
  "summary": "Request for information about project management tools and pricing.",
  "next_steps": [
    "Send product brochure",
    "Schedule demo call",
    "Follow up in 2 business days"
  ]
}
```

## 3. JSON Invoice Processing

File: `invoice_processing.log`
```
=== Processing JSON Invoice ===
[Classifier] Detected format: JSON, intent: Invoice
[JSON Agent] Extracted invoice details
- Invoice ID: INV-2025-1001
- Amount: $1,250.00
- Due Date: 2025-06-30
[Memory Log] Added entry with ID: ghi789-012-345

=== Processing Result ===
{
  "status": "success",
  "classification": {
    "format": "JSON",
    "intent": "Invoice"
  },
  "invoice_id": "INV-2025-1001",
  "amount": 1250.00,
  "currency": "USD",
  "due_date": "2025-06-30",
  "status": "pending",
  "next_steps": [
    "Send payment reminder 7 days before due date",
    "Process payment on due date"
  ]
}
```

## 4. PDF Document Processing

File: `pdf_processing.log`
```
=== Processing PDF Document ===
[Classifier] Detected format: PDF, intent: Regulation
[PDF Agent] Extracted 5 pages of content
[PDF Agent] Detected document type: Compliance Policy
[Memory Log] Added entry with ID: jkl012-345-678

=== Processing Result ===
{
  "status": "success",
  "classification": {
    "format": "PDF",
    "intent": "Regulation"
  },
  "document_type": "Compliance Policy",
  "pages_processed": 5,
  "key_topics": [
    "Data Protection",
    "Privacy Compliance",
    "Security Standards"
  ],
  "compliance_status": "Meets Requirements",
  "next_steps": [
    "Review with legal team",
    "Schedule compliance training",
    "Update policy documentation"
  ]
}
```

## Understanding the Outputs

Each processing result includes:
- **Classification**: Format and intent detected
- **Extracted Information**: Key data points from the document
- **Urgency Level**: For emails, indicates priority
- **Next Steps**: Suggested actions based on document type
- **Memory Log**: Reference ID for tracking in the system

These samples demonstrate the system's ability to handle various document types and extract relevant information for further processing.
