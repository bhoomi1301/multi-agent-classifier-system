
import json
import logging
from typing import Dict, Any, Optional
import ollama

class LLMService:
    def __init__(self, model_name: str = "mistral"):
        """
        Initialize the LLM service with a specific model.
        
        Args:
            model_name: Name of the Ollama model to use (default: "mistral")
        """
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        
        # Verify the model is available
        self._verify_model()
    
    def _verify_model(self):
        """Verify that the specified model is available, try to pull if not."""
        try:
            # List all available models
            response = ollama.list()
            
            # Extract model names from the response
            model_names = []
            if isinstance(response, dict) and 'models' in response:
                for model in response['models']:
                    if 'model' in model:  # Check for 'model' key instead of 'name'
                        model_name = model['model'].split(':')[0]  # Handle format 'model:tag'
                        model_names.append(model_name)
            
            self.logger.debug(f"Available models: {model_names}")
            
            # Check if our model is available
            if self.model_name not in model_names:
                self.logger.info(f"Model '{self.model_name}' not found. Attempting to pull...")
                ollama.pull(self.model_name)
                self.logger.info(f"Successfully pulled model '{self.model_name}'")
            else:
                self.logger.info(f"Model '{self.model_name}' is available")
                
        except Exception as e:
            self.logger.error(f"Error verifying/pulling model: {str(e)}")
            self.logger.error(f"Response structure: {response}" if 'response' in locals() else "No response received")
            # Continue anyway - the model might still work if it's a local file
            self.logger.warning("Continuing with model verification skipped")
    
    async def generate_text(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Generate text using the Ollama model.
        
        Args:
            prompt: The input prompt
            system_prompt: Optional system message to set the behavior
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            json_mode: If True, expects JSON response and tries to parse it
            
        Returns:
            Dictionary containing the generated text and metadata
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # Format the request for Ollama
            options = {
                "temperature": temperature,
                "num_predict": max_tokens,
                "format": "json" if json_mode else None
            }
            
            # Remove None values from options
            options = {k: v for k, v in options.items() if v is not None}
            
            # Make the request to Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options=options
            )
            
            content = response['message']['content']
            
            # Try to parse JSON if in JSON mode
            if json_mode:
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse JSON response, returning raw text")
            
            return {
                "content": content,
                "model": self.model_name,
                "tokens_used": response.get('eval_count', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            raise
    
    async def classify_intent(self, text: str) -> Dict[str, Any]:
        """
        Classify the intent of the input text.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary with classification results
        """
        system_prompt = """You are an intent classification system. Analyze the input text and determine its intent.
        Possible intents are: ["rfq" (request for quote), "complaint", "regulation", "other"]
        
        Respond with a JSON object containing:
        {
            "intent": "one_of_the_possible_intents",
            "confidence": 0.0-1.0,
            "reasoning": "brief_explanation"
        }"""
        
        response = await self.generate_text(
            prompt=text,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent classifications
            json_mode=True
        )
        
        return response.get('content', {})

    async def extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract relevant entities from the text based on the intent.
        
        Args:
            text: Input text
            intent: The classified intent
            
        Returns:
            Dictionary with extracted entities
        """
        system_prompt = f"""You are an information extraction system. Extract relevant entities from the text based on the intent: {intent}.
        
        For each intent, extract these fields:
        - rfq: product_name, quantity, deadline, contact_info
        - complaint: issue_description, severity, contact_info, desired_resolution
        - regulation: regulation_name, compliance_status, affected_areas
        - other: key_points, action_items
        
        Return a JSON object with the extracted fields."""
        
        response = await self.generate_text(
            prompt=text,
            system_prompt=system_prompt,
            temperature=0.2,  # Low temperature for consistent extraction
            json_mode=True
        )
        
        return response.get('content', {})
