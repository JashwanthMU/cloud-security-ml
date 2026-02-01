"""
LLM-based Context Analyzer
Uses AI to understand intent behind infrastructure configurations
"""

import json
from openai import OpenAI
from llm_config import LLMConfig

class LLMAnalyzer:
    """
    Analyzes Terraform configurations using LLM for context understanding
    """
    
    def __init__(self):
        config = LLMConfig()
        self.config = config.get_config()
        
        if self.config['provider'] == 'openai':
            self.client = OpenAI(api_key=self.config['api_key'])
            self.model = self.config['model']
        # Bedrock support will be added when access granted
    
    def analyze_intent(self, terraform_code, resource_name, features):
        """
        Analyze configuration intent using LLM
        
        Args:
            terraform_code: Raw Terraform code string
            resource_name: Name of the resource
            features: Dict of extracted security features
        
        Returns:
            Dict with intent analysis
        """
        
        # Create specialized prompt
        prompt = self._create_security_prompt(
            terraform_code, 
            resource_name, 
            features
        )
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert cloud security architect analyzing infrastructure code for security risks."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent analysis
            max_tokens=600
        )
        
        # Parse response
        analysis_text = response.choices[0].message.content
        
        return self._parse_llm_response(analysis_text)
    
    def _create_security_prompt(self, code, name, features):
        """
        Creates a specialized prompt for security analysis
        
        Uses few-shot prompting with examples
        """
        
        prompt = f"""Analyze this Terraform configuration for security risks.

**CONFIGURATION:**
```hcl
{code}
```

**RESOURCE NAME:** {name}

**DETECTED PROPERTIES:**
- Public Access: {"YES" if features['public_access'] else "NO"}
- Encryption: {"Enabled" if features['encryption_enabled'] else "Disabled"}
- Versioning: {"Enabled" if features['versioning_enabled'] else "Disabled"}
- Logging: {"Enabled" if features['logging_enabled'] else "Disabled"}
- Sensitive Naming: {"YES" if features['sensitive_naming'] else "NO"}

**YOUR TASK:**
Analyze this configuration and determine:

1. **Intent Classification:**
   - Is this INTENTIONALLY risky (e.g., public website bucket) or ACCIDENTALLY risky (e.g., exposed customer data)?
   
2. **Purpose Inference:**
   - What is the likely business purpose based on resource name and configuration?
   
3. **Risk Assessment:**
   - What are the top 3 security concerns?
   - What could go wrong if this is compromised?
   
4. **Risk Scoring:**
   - On a scale of 0.0 (completely safe) to 1.0 (critical risk), rate this configuration

**EXAMPLES FOR REFERENCE:**

Example 1 - INTENTIONAL (Low Risk):
Resource: "marketing_website"
Config: public-read bucket with website hosting
Intent: INTENTIONAL - Clearly meant to be public for website hosting
Risk Score: 0.25

Example 2 - ACCIDENTAL (High Risk):
Resource: "customer_database_backup"
Config: public-read bucket, no encryption
Intent: ACCIDENTAL - Sensitive data should never be public
Risk Score: 0.95

Example 3 - AMBIGUOUS (Medium Risk):
Resource: "data_lake"
Config: public bucket with encryption
Intent: UNCERTAIN - Could be intentional for data sharing, needs approval
Risk Score: 0.55

**OUTPUT FORMAT (respond in this exact JSON format):**
```json
{{
  "intent": "INTENTIONAL" or "ACCIDENTAL" or "UNCERTAIN",
  "purpose": "<1-2 sentence description of inferred business purpose>",
  "concerns": [
    "<concern 1>",
    "<concern 2>",
    "<concern 3>"
  ],
  "blast_radius": "<what could be compromised if breached>",
  "llm_risk_score": <0.0-1.0>,
  "reasoning": "<2-3 sentence detailed explanation>",
  "recommendation": "BLOCK" or "WARN" or "ALLOW"
}}
```

Think step-by-step and provide thorough analysis."""

        return prompt
    
    def _parse_llm_response(self, text):
        """
        Parse LLM response into structured format
        
        Handles both JSON and natural language responses
        """
        
        try:
            # Try to find JSON in response
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                result = json.loads(json_str)
                
                # Validate required fields
                required = ['intent', 'purpose', 'concerns', 'llm_risk_score', 'reasoning']
                if all(field in result for field in required):
                    return result
        
        except json.JSONDecodeError:
            pass
        
        # Fallback: return default structure
        return {
            'intent': 'UNCERTAIN',
            'purpose': 'Unable to determine from LLM response',
            'concerns': ['Parse error in LLM response'],
            'blast_radius': 'Unknown',
            'llm_risk_score': 0.5,
            'reasoning': text,
            'recommendation': 'WARN'
        }

# Test the analyzer
if __name__ == '__main__':
    
    analyzer = LLMAnalyzer()
    
    # Test Case 1: Intentional public website
    test_code_1 = '''
resource "aws_s3_bucket" "marketing_site" {
  bucket = "company-public-website"
  acl    = "public-read"
  
  website {
    index_document = "index.html"
    error_document = "error.html"
  }
  
  tags = {
    Purpose = "Marketing website hosting"
    Public  = "Yes - approved by marketing team"
  }
}
'''
    
    features_1 = {
        'public_access': 1,
        'encryption_enabled': 0,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 0,
        'has_tags': 1
    }
    
    print("=" * 60)
    print("TEST 1: Intentional Public Website")
    print("=" * 60)
    
    result_1 = analyzer.analyze_intent(test_code_1, "marketing_site", features_1)
    
    print(f"\nIntent: {result_1['intent']}")
    print(f"Purpose: {result_1['purpose']}")
    print(f"LLM Risk Score: {result_1['llm_risk_score']}")
    print(f"Recommendation: {result_1['recommendation']}")
    print(f"\nReasoning: {result_1['reasoning']}")
    print(f"\nConcerns:")
    for concern in result_1['concerns']:
        print(f"  - {concern}")
    
    print("\n" + "=" * 60)
    print("TEST 2: Accidental Public Customer Data")
    print("=" * 60)
    
    # Test Case 2: Accidental exposure
    test_code_2 = '''
resource "aws_s3_bucket" "customer_data" {
  bucket = "prod-customer-database-backup"
  acl    = "public-read"
}
'''
    
    features_2 = {
        'public_access': 1,
        'encryption_enabled': 0,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 1,
        'has_tags': 0
    }
    
    result_2 = analyzer.analyze_intent(test_code_2, "customer_data", features_2)
    
    print(f"\nIntent: {result_2['intent']}")
    print(f"Purpose: {result_2['purpose']}")
    print(f"LLM Risk Score: {result_2['llm_risk_score']}")
    print(f"Recommendation: {result_2['recommendation']}")
    print(f"\nReasoning: {result_2['reasoning']}")
    print(f"\nConcerns:")
    for concern in result_2['concerns']:
        print(f"  - {concern}")
    print(f"\nBlast Radius: {result_2['blast_radius']}")