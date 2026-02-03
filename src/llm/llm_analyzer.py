"""
LLM-based Context Analyzer
Uses AI to understand intent behind configurations
"""

import json
import os
from openai import OpenAI

class LLMAnalyzer:
    """Analyzes Terraform using AI for context understanding"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
        else:
            print("⚠️  OpenAI API key not found - LLM analysis disabled")
            self.enabled = False
    
    def analyze_intent(self, terraform_code, resource_name, features):
        """
        Analyze configuration intent using LLM
        
        Args:
            terraform_code: Raw Terraform code
            resource_name: Name of resource
            features: Extracted security features dict
        
        Returns:
            Dict with intent analysis
        """
        
        if not self.enabled:
            return self._get_fallback_analysis(features)
        
        try:
            prompt = self._create_prompt(terraform_code, resource_name, features)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cloud security expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            return self._parse_response(result)
        
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self._get_fallback_analysis(features)
    
    def _create_prompt(self, code, name, features):
        """Create analysis prompt"""
        
        return f"""Analyze this Terraform configuration:
```
{code}
```

Resource: {name}
Public Access: {"YES" if features.get('public_access') else "NO"}
Encrypted: {"YES" if features.get('encryption_enabled') else "NO"}
Sensitive Naming: {"YES" if features.get('sensitive_naming') else "NO"}

Determine:
1. Is this INTENTIONAL or ACCIDENTAL risk?
2. What's the business purpose?
3. Risk score (0.0-1.0)

Respond in JSON:
{{
  "intent": "INTENTIONAL|ACCIDENTAL|UNCERTAIN",
  "purpose": "brief description",
  "llm_risk_score": 0.0-1.0,
  "reasoning": "explanation",
  "concerns": ["concern1", "concern2"]
}}"""
    
    def _parse_response(self, text):
        """Parse LLM JSON response"""
        
        try:
            # Find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            json_str = text[start:end]
            return json.loads(json_str)
        except:
            return {
                'intent': 'UNCERTAIN',
                'purpose': 'Parse error',
                'llm_risk_score': 0.5,
                'reasoning': text,
                'concerns': []
            }
    
    def _get_fallback_analysis(self, features):
        """Fallback when LLM unavailable"""
        
        risk = 0.0
        if features.get('public_access'):
            risk += 0.4
        if not features.get('encryption_enabled'):
            risk += 0.3
        if features.get('sensitive_naming'):
            risk += 0.2
        
        return {
            'intent': 'UNCERTAIN',
            'purpose': 'LLM analysis unavailable',
            'llm_risk_score': risk,
            'reasoning': 'Using rule-based fallback',
            'concerns': ['LLM API not configured']
        }

# Test
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    analyzer = LLMAnalyzer()
    
    test_code = '''
resource "aws_s3_bucket" "data" {
  bucket = "customer-database"
  acl    = "public-read"
}
'''
    
    features = {
        'public_access': 1,
        'encryption_enabled': 0,
        'sensitive_naming': 1
    }
    
    result = analyzer.analyze_intent(test_code, "data", features)
    print(json.dumps(result, indent=2))