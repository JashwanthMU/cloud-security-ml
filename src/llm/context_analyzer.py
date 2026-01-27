"""
Context Analyzer - Uses LLM to understand infrastructure intent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llm.llm_wrapper import LLMWrapper

class ContextAnalyzer:
    def __init__(self, verbose=False):
        self.llm = LLMWrapper(verbose=verbose)
        self.verbose = verbose
    
    def analyze(self, terraform_code, resource_name, features):
        """
        Analyze infrastructure code for security context
        
        Returns:
        {
            'intent': 'intentional' or 'accidental',
            'purpose': 'description',
            'llm_risk_score': 0.0-1.0,
            'reasoning': 'explanation',
            'concerns': ['concern1', ...]
        }
        """
        
        prompt = self._create_prompt(terraform_code, resource_name, features)
        
        try:
            response = self.llm.generate(prompt, max_tokens=600)
            return self._parse_response(response)
        except Exception as e:
            return {
                'intent': 'unknown',
                'purpose': 'Analysis failed',
                'llm_risk_score': 0.5,
                'reasoning': f'Error: {e}',
                'concerns': []
            }
    
    def _create_prompt(self, code, name, features):
        features_text = f"""- Public: {"Yes ⚠️" if features.get('public_access') else "No ✓"}
- Encryption: {"Yes ✓" if features.get('encryption_enabled') else "No ⚠️"}
- Sensitive Name: {"Yes ⚠️" if features.get('sensitive_naming') else "No ✓"}"""
        
        return f"""Analyze this Terraform configuration:

CODE:
```
{code}
```

RESOURCE: {name}

FEATURES:
{features_text}

Determine:
1. INTENT: intentional or accidental?
2. PURPOSE: What's this for? (1 sentence)
3. RISK_SCORE: 0.0 (safe) to 1.0 (dangerous)
4. CONCERNS: List issues (or "None")
5. REASONING: Why this risk score?

Format:
INTENT: [intentional/accidental]
PURPOSE: [description]
RISK_SCORE: [0.0-1.0]
CONCERNS: [concern1] | [concern2]
REASONING: [explanation]"""
    
    def _parse_response(self, text):
        result = {
            'intent': 'unknown',
            'purpose': '',
            'llm_risk_score': 0.5,
            'concerns': [],
            'reasoning': text
        }
        
        for line in text.split('\n'):
            line = line.strip()
            
            if line.upper().startswith('INTENT:'):
                intent = line.split(':', 1)[1].strip().lower()
                result['intent'] = 'intentional' if 'intentional' in intent else 'accidental'
            
            elif line.upper().startswith('PURPOSE:'):
                result['purpose'] = line.split(':', 1)[1].strip()
            
            elif line.upper().startswith('RISK_SCORE:'):
                try:
                    score = float(line.split(':', 1)[1].strip())
                    result['llm_risk_score'] = max(0.0, min(1.0, score))
                except:
                    pass
            
            elif line.upper().startswith('CONCERNS:'):
                concerns = line.split(':', 1)[1].strip()
                if concerns.lower() != 'none':
                    result['concerns'] = [c.strip() for c in concerns.split('|')]
            
            elif line.upper().startswith('REASONING:'):
                result['reasoning'] = line.split(':', 1)[1].strip()
        
        return result

# Test
if __name__ == '__main__':
    analyzer = ContextAnalyzer(verbose=True)
    
    test_code = '''
resource "aws_s3_bucket" "website" {
  bucket = "company-marketing-site"
  acl    = "public-read"
  
  website {
    index_document = "index.html"
  }
}
'''
    
    features = {
        'public_access': 1,
        'encryption_enabled': 0,
        'sensitive_naming': 0
    }
    
    result = analyzer.analyze(test_code, "website", features)
    
    print(f"\nIntent: {result['intent']}")
    print(f"Purpose: {result['purpose']}")
    print(f"LLM Risk: {result['llm_risk_score']}")
    print(f"Reasoning: {result['reasoning']}")