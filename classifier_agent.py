import requests
import json
import os
import re

class ClassifierAgent:
    def __init__(self, model_url="http://localhost:11434/api/generate", model_name="mistral"):
        self.model_url = model_url
        self.model_name = model_name

    def classify(self, input_text, source_hint="Unknown"):
        # Ensure input is a string for the prompt
        input_str = self._ensure_str(input_text)
        
        prompt = f"""
You are a smart document classification assistant. The following content is from a **{source_hint}** source.

Your task is to analyze the content and classify it with the most appropriate format and intent.

Available formats:
- "PDF" - For PDF documents
- "Email" - For email messages
- "JSON" - For JSON data

Available intents:
- "Invoice" - For billing or payment-related documents
- "RFQ" - For formal requests for quotes with specific product/service requirements and quantities
- "Complaint" - For customer complaints or negative feedback
- "Inquiry" - For general information requests or questions
- "Support" - For technical support requests
- "Sales" - For sales-related questions about products/pricing
- "Regulation" - For compliance or legal matters
- "Other" - When none of the above apply

Important guidelines:
- Only classify as "RFQ" if it's a formal request for quote with specific product/service requirements.
- Use "Inquiry" for general information requests about products/services.
- Use "Sales" for pricing or sales-related questions.

Return a JSON object with "format" and "intent" fields. Only return the JSON, no other text.

Content to classify:
"""
        prompt += f"""
{input_str}
"""
        prompt += """
Return the classification JSON:"""

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(self.model_url, json=payload, timeout=20)
            response.raise_for_status()
            result = response.json()["response"].strip()
            print("Raw response from model:\n", result)
            return self._extract_json(result)
        except requests.exceptions.Timeout:
            print("[Classifier] Timeout while waiting for model response.")
        except requests.exceptions.RequestException as e:
            print(f"[Classifier] Request failed: {e}")
        except Exception as e:
            print(f"[Classifier] Unexpected error: {e}")

        # Fallback classification based on file extension and content analysis
        print("[Classifier] Using fallback classification based on content analysis.")
        return self._fallback_classify(input_text, source_hint)

    def _extract_json(self, text):
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception as e:
            print("Error parsing JSON:", e)
            return {"format": "Unknown", "intent": "Unknown"}
            
    def _fallback_classify(self, input_text, source_hint):
        """Fallback classification when LLM is not available"""
        # Ensure input_text is a string for JSON parsing
        input_str = self._ensure_str(input_text)
        
        # Check if source is a file path with JSON extension
        if isinstance(source_hint, str) and source_hint.lower().endswith('.json'):
            return {"format": "JSON", "intent": self._detect_json_intent(input_str)}
            
        # Check if input is valid JSON
        try:
            data = json.loads(input_str)
            if isinstance(data, dict):
                return {"format": "JSON", "intent": self._detect_json_intent(input_str)}
        except (json.JSONDecodeError, TypeError):
            pass
            
        return {"format": "Email", "intent": self._detect_email_intent(input_str)}
    
    def _detect_json_intent(self, content):
        """Detect intent from JSON content"""
        content_str = self._ensure_str(content)
        content_lower = content_str.lower()
        
        # Check for invoice indicators
        if any(term in content_lower for term in ['invoice_id', 'invoice_', 'total', 'subtotal', 'tax_amount']):
            return "Invoice"
            
        # Check for RFQ indicators
        if any(term in content_lower for term in ['rfq_id', 'request for quote', 'request_for_quote']):
            return "RFQ"
            
        # Default to Other if no specific intent detected
        return "Other"
    
    def _ensure_str(self, content):
        """Ensure content is a string, decoding bytes if necessary"""
        if isinstance(content, bytes):
            try:
                return content.decode('utf-8', errors='ignore')
            except:
                return str(content)
        return str(content)
        
    def _detect_email_intent(self, content):
        """Detect intent from email content"""
        content_str = self._ensure_str(content)
        content_lower = content_str.lower()
        
        # Check for complaint indicators
        complaint_terms = [
            'complaint', 'dissatisfied', 'unhappy', 'not satisfied',
            'issue with', 'problem with', 'not working', 'disappointed',
            'poor service', 'bad experience', 'terrible', 'awful', 'horrible'
        ]
        if any(term in content_lower for term in complaint_terms):
            return "Complaint"
            
        # Check for inquiry/intent to purchase
        inquiry_terms = [
            'information about', 'interested in', 'would like to know',
            'can you tell me', 'looking for', 'need more info',
            'more information', 'details about', 'pricing for',
            'demo', 'trial', 'free trial', 'schedule a call', 'set up a meeting'
        ]
        if any(term in content_lower for term in inquiry_terms):
            return "Inquiry"
            
        # Check for support request
        support_terms = [
            'help with', 'support', 'not working', 'how to', 'question about',
            'trouble with', 'having issues', 'need help', 'can\'t find',
            'unable to', 'having trouble'
        ]
        if any(term in content_lower for term in support_terms):
            return "Support"
            
        # Check for sales related
        sales_terms = [
            'quote', 'pricing', 'price list', 'cost of', 'how much',
            'discount', 'special offer', 'promotion', 'deal',
            'enterprise plan', 'business plan', 'pricing plan'
        ]
        if any(term in content_lower for term in sales_terms):
            return "Sales"
            
        # Check for regulation/compliance
        regulation_terms = [
            'regulation', 'compliance', 'requirement', 'standard',
            'gdpr', 'ccpa', 'hipaa', 'pci dss', 'iso 27001', 'soc 2',
            'data protection', 'privacy policy', 'legal requirement'
        ]
        if any(term in content_lower for term in regulation_terms):
            return "Regulation"
            
        # Default to Other if no specific intent detected
        return "Other"
