# pdf_agent.py

import re
import fitz  # PyMuPDF
import requests

from classifier_agent import ClassifierAgent
from json_agent import JSONAgent
from rfq_agent import process_rfq
from complaint_agent import process_complaint
from regulation_agent import process_regulation
from other_agent import process_other
from memory_store import MemoryStore

class PDFAgent:
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.json_agent = JSONAgent(memory)
        self.classifier = ClassifierAgent()

    def detect_intent_with_ollama(self, text):
        # First try pattern matching for common document types
        text_lower = text.lower().strip()
        
        # Enhanced invoice pattern matching
        invoice_terms = [
            'invoice', 'bill', 'payment', 'amount', 'total', 'subtotal',
            'tax', 'due', 'balance', 'payable', 'charges', 'fee', 'cost',
            'price', 'payment terms', 'net amount', 'gross amount', 'vat',
            'gst', 'taxable', 'line item', 'item', 'quantity', 'unit price',
            'extended price', 'subtotal', 'shipping', 'handling'
        ]
        
        # Check for invoice patterns with multiple indicators
        invoice_indicators = sum(1 for term in invoice_terms if term in text_lower)
        
        # If we find multiple invoice-related terms, it's likely an invoice
        if invoice_indicators >= 3:
            return "invoice"
            
        # Check for specific invoice patterns
        if any(re.search(r'invoice\s*(?:no|#|number)[:\s]*(\w+)', text_lower, re.IGNORECASE)):
            if any(term in text_lower for term in ['amount', 'total', 'subtotal', 'tax']):
                return "invoice"
                
        # Check for RFQ patterns
        rfq_terms = [
            'request for quote', 'rfq', 'quotation request', 'price quote',
            'request for proposal', 'rfp', 'request for bid', 'rfq number',
            'quote request', 'bidding', 'tender', 'proposal request'
        ]
        if any(term in text_lower for term in rfq_terms):
            return "rfq"
            
        # If no clear pattern, try the LLM with a shorter timeout
        try:
            # Truncate text to first 1000 chars to avoid timeout
            truncated_text = text[:1000] + '...' if len(text) > 1000 else text
            
            prompt = """
Analyze the following document text and classify its intent. 
Respond with ONLY one word from this list: invoice, rfq, complaint, regulation, other

Document:"""
            prompt += f"\n\n{truncated_text}\n\n"
            prompt += "Intent: "
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.0}  # Make it more deterministic
                },
                timeout=5  # Shorter timeout
            )
            
            if response.status_code == 200:
                output = response.json().get("response", "").strip().lower()
                # Clean up the response to get just the first word
                output = output.split()[0] if output else ""
                if output in ["invoice", "rfq", "complaint", "regulation"]:
                    return output
                    
        except requests.exceptions.Timeout:
            print("[Classifier] LLM request timed out")
        except Exception as e:
            print(f"[Classifier] Error using LLM: {str(e)}")
        
        # Final fallback - check for common invoice patterns
        if any(term in text_lower for term in ['invoice', 'bill', 'payment']) and \
           any(term in text_lower for term in ['amount', 'total', '$']):
            return "invoice"
            
        return "other"

    def extract_text_from_pdf(self, pdf_input):
        """Extract text from PDF file or process text content directly.
        
        Args:
            pdf_input: Either a file path (str) or direct text content
            
        Returns:
            str: Extracted text or error message
        """
        # If input is already text, return it directly
        if isinstance(pdf_input, str) and '\n' in pdf_input and any(
            marker in pdf_input.lower() 
            for marker in ['invoice', 'date', 'vendor', 'amount']
        ):
            return pdf_input
            
        # Otherwise, treat as file path
        try:
            doc = fitz.open(pdf_input)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return f"[ERROR] Failed to read PDF: {str(e)}"

    def extract_invoice_fields(self, text):
        invoice_id = re.search(r'Invoice No[:\s]*([A-Z0-9\-]+)', text, re.I)
        date = re.search(r'Date[:\s]*([\d\-\/]+)', text, re.I)
        vendor = re.search(r'Vendor[:\s]*(.+)', text, re.I)
        amount = re.search(r'Amount[:\s]*\$?([\d,\.]+)', text, re.I)

        invoice_id_val = invoice_id.group(1) if invoice_id else None
        date_val = date.group(1) if date else None
        vendor_val = vendor.group(1).strip() if vendor else None

        amount_val = None
        if amount:
            try:
                amount_val = float(amount.group(1).replace(',', ''))
            except ValueError:
                amount_val = None

        missing_fields = [
            k for k, v in {
                "invoice_id": invoice_id_val,
                "date": date_val,
                "vendor": vendor_val,
                "amount": amount_val,
            }.items() if not v
        ]

        return {
            "invoice_id": invoice_id_val,
            "date": date_val,
            "vendor": vendor_val,
            "amount": amount_val,
            "missing_fields": missing_fields
        }

    def process_pdf(self, text, classification=None, conversation_id=None, sender=None):
        """Process PDF text content.
        
        Args:
            text: Extracted text from PDF
            classification: Optional classification dict with format and intent
            conversation_id: Optional conversation ID
            sender: Optional sender information
            
        Returns:
            dict: Processing results with extracted information
        """
        if text.startswith("[ERROR]"):
            return {"error": text}
            
        # Detect intent if not provided
        intent = None
        if classification and 'intent' in classification:
            intent = classification.get('intent').lower()
        else:
            intent = self.detect_intent_with_ollama(text)
            classification = {"format": "PDF", "intent": intent}
        
        # Initialize result with basic information
        result = {
            "classification": classification,
            "content": text,
            "intent": intent,
            "processed_data": {}
        }
        
        # Process based on detected intent
        if intent == "invoice":
            # Extract invoice fields
            invoice_data = self.extract_invoice_fields(text)
            
            # Check for anomalies
            anomalies = []
            amount = invoice_data.get("amount")
            if amount is None or amount <= 0:
                anomalies.append("Amount missing or invalid")
            
            # Update result with invoice data
            result["processed_data"].update(invoice_data)
            if anomalies:
                result["anomalies"] = anomalies
            
            # Add raw text if needed
            if "raw_text" not in result["processed_data"]:
                result["processed_data"]["raw_text"] = text
                
        elif intent == "rfq":
            result["processed_data"] = process_rfq(text, self.memory)
        elif intent == "complaint":
            result["processed_data"] = process_complaint(text, self.memory)
        elif intent == "regulation":
            result["processed_data"] = process_regulation(text, self.memory)
        else:
            result["processed_data"] = process_other(text, self.memory)
        
        # Log to memory
        self.memory.log("PDF", result, conversation_id=conversation_id, sender=sender)
        return result
