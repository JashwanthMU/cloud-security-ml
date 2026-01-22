"""
Context Analyzer - Uses LLM to understand infrastructure intent
Determines if a configuration is intentionally risky or accidentally dangerous
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from llm.llm_wrapper import LLMWrapper

class ContextAnalyzer:
    """
    Uses Large Language Model to analyze infrastructure configurations
    for security context, intent, and risk assessment
    """
    
    def __init__(self, verbose=False):
        """
        Initialize context analyzer
        
        Args:
            verbose: If True, print detailed logs
        """
        self.llm = LLMWrapper(verbose=verbose)
        self.verbose = verbose
    
    def analyze(self, terraform_code, resource_name, features):
        """
        Analyze infrastructure code for security context
        
        Args:
            terraform_code: Raw Terraform code string
            resource_name: Name of the resource being analyzed
            features: Dictionary of extracted security features
        
        Returns:
            {
                'intent': 'intentional' or 'accidental',
                'purpose': 'Brief description of purpose',
                'llm_risk_score': 0.0-1.0 risk score,
                'reasoning': 'Detailed explanation',
                'concerns': ['concern1', 'concern2', ...],
                'confidence': 0.0-1.0
            }
        """
        
        if self.verbose:
            print(f"\n🤖 Analyzing context for: {resource_name}")
        
        # Create detailed prompt
        prompt = self._create_analysis_prompt(
            terraform_code,
            resource_name,
            features
        )
        
        # Call LLM
        try:
            response = self.llm.generate(prompt, max_tokens=600, temperature=0.1)
            
            if self.verbose:
                print(f"   ✅ LLM analysis complete")
            
            # Parse response
            result = self._parse_response(response)
            
            return result
        
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️  LLM error: {e}")
            
            # Return safe defaults if LLM fails
            return {
                'intent': 'unknown',
                'purpose': 'Could not analyze (LLM unavailable)',
                'llm_risk_score': 0.5,
                'reasoning': f'LLM analysis failed: {str(e)}',
                'concerns': ['Unable to perform AI analysis'],
                'confidence': 0.3
            }
    
    def _create_analysis_prompt(self, code, name, features):
        """
        Create detailed security analysis prompt for LLM
        """
        
        # Format features for display
        features_text = f"""- Public Access: {"Yes ⚠️" if features.get('public_access') else "No ✓"}
- Encryption: {"Enabled ✓" if features.get('encryption_enabled') else "Disabled ⚠️"}
- Versioning: {"Enabled ✓" if features.get('versioning_enabled') else "Disabled ⚠️"}
- Logging: {"Enabled ✓" if features.get('logging_enabled') else "Disabled ⚠️"}
- Sensitive Naming: {"Yes ⚠️" if features.get('sensitive_naming') else "No ✓"}
- Has Tags: {"Yes ✓" if features.get('has_tags') else "No ⚠️"}"""
        
        prompt = f"""You are a cloud security expert analyzing infrastructure-as-code for security risks.

TERRAFORM CONFIGURATION:
```
{code}
```

RESOURCE NAME: {name}

AUTOMATED SECURITY SCAN RESULTS:
{features_text}

YOUR TASK:
Analyze this configuration and determine:

1. INTENT: Is this configuration:
   - "intentional" (legitimate business use, e.g., public website, CDN)
   - "accidental" (likely a security mistake or oversight)

2. PURPOSE: What is the business purpose of this resource? (1-2 sentences)

3. RISK ASSESSMENT: Rate the security risk from 0.0 to 1.0:
   - 0.0-0.3 = Low risk (safe configuration)
   - 0.3-0.7 = Medium risk (needs review)
   - 0.7-1.0 = High risk (likely breach risk)

4. CONCERNS: List the top 3 security concerns. If none, write "None"

5. REASONING: Explain your risk assessment in 2-3 sentences

IMPORTANT CONTEXT CLUES:
- Resource names like "website", "cdn", "public-assets" suggest intentional public access
- Names like "customer", "database", "backup", "private" suggest accidental exposure
- Tags and comments provide intent (e.g., "Purpose: Public website")
- Configuration completeness (encryption, versioning, logging) indicates care level

RESPOND IN THIS EXACT FORMAT (no markdown, no code blocks):
INTENT: [intentional/accidental]
PURPOSE: [description]
RISK_SCORE: [0.0-1.0]
CONCERNS: [concern1] | [concern2] | [concern3]
REASONING: [explanation]
CONFIDENCE: [0.0-1.0]

Be specific and reference actual values from the configuration."""

        return prompt
    
    def _parse_response(self, response_text):
        """
        Parse LLM response into structured format
        """
        
        result = {
            'intent': 'unknown',
            'purpose': '',
            'llm_risk_score': 0.5,
            'concerns': [],
            'reasoning': response_text,
            'confidence': 0.7
        }
        
        try:
            # Split into lines
            lines = response_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Parse INTENT
                if line.upper().startswith('INTENT:'):
                    intent_text = line.split(':', 1)[1].strip().lower()
                    if 'intentional' in intent_text:
                        result['intent'] = 'intentional'
                    elif 'accidental' in intent_text:
                        result['intent'] = 'accidental'
                
                # Parse PURPOSE
                elif line.upper().startswith('PURPOSE:'):
                    result['purpose'] = line.split(':', 1)[1].strip()
                
                # Parse RISK_SCORE
                elif line.upper().startswith('RISK_SCORE:'):
                    score_text = line.split(':', 1)[1].strip()
                    try:
                        score = float(score_text)
                        result['llm_risk_score'] = max(0.0, min(1.0, score))
                    except:
                        result['llm_risk_score'] = 0.5
                
                # Parse CONCERNS
                elif line.upper().startswith('CONCERNS:'):
                    concerns_text = line.split(':', 1)[1].strip()
                    if concerns_text.lower() != 'none':
                        result['concerns'] = [
                            c.strip() 
                            for c in concerns_text.split('|')
                            if c.strip()
                        ]
                
                # Parse REASONING
                elif line.upper().startswith('REASONING:'):
                    result['reasoning'] = line.split(':', 1)[1].strip()
                
                # Parse CONFIDENCE
                elif line.upper().startswith('CONFIDENCE:'):
                    conf_text = line.split(':', 1)[1].strip()
                    try:
                        conf = float(conf_text)
                        result['confidence'] = max(0.0, min(1.0, conf))
                    except:
                        result['confidence'] = 0.7
        
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️  Parse warning: {e}")
        
        return result

# Test the analyzer
if __name__ == '__main__':
    print("\n" + "="*70)
    print("  CONTEXT ANALYZER TEST")
    print("="*70 + "\n")
    
    analyzer = ContextAnalyzer(verbose=True)
    
    # Test Case 1: Intentional public website
    print("\n" + "="*70)
    print("TEST 1: Intentional Public Website")
    print("="*70)
    
    test1_code = '''
resource "aws_s3_bucket" "marketing_website" {
  bucket = "company-public-marketing-site"
  acl    = "public-read"
  
  website {
    index_document = "index.html"
    error_document = "error.html"
  }
  
  tags = {
    Purpose     = "Public Website"
    Environment = "Production"
    Team        = "Marketing"
  }
}
'''
    
    test1_features = {
        'public_access': 1,
        'encryption_enabled': 0,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 0,
        'has_tags': 1
    }
    
    result1 = analyzer.analyze(test1_code, "marketing_website", test1_features)
    
    print(f"\n📊 RESULTS:")
    print(f"   Intent: {result1['intent']}")
    print(f"   Purpose: {result1['purpose']}")
    print(f"   LLM Risk Score: {result1['llm_risk_score']:.2f}")
    print(f"   Confidence: {result1['confidence']:.2f}")
    print(f"   Concerns: {', '.join(result1['concerns']) if result1['concerns'] else 'None'}")
    print(f"   Reasoning: {result1['reasoning']}")
    
    # Test Case 2: Accidental public customer data
    print("\n" + "="*70)
    print("TEST 2: Accidental Public Customer Data")
    print("="*70)
    
    test2_code = '''
resource "aws_s3_bucket" "data_backup" {
  bucket = "customer-database-backup-prod"
  acl    = "public-read"
}
'''
    
    test2_features = {
        'public_access': 1,
        'encryption_enabled': 0,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 1,
        'has_tags': 0
    }
    
    result2 = analyzer.analyze(test2_code, "data_backup", test2_features)
    
    print(f"\n📊 RESULTS:")
    print(f"   Intent: {result2['intent']}")
    print(f"   Purpose: {result2['purpose']}")
    print(f"   LLM Risk Score: {result2['llm_risk_score']:.2f}")
    print(f"   Confidence: {result2['confidence']:.2f}")
    print(f"   Concerns: {', '.join(result2['concerns']) if result2['concerns'] else 'None'}")
    print(f"   Reasoning: {result2['reasoning']}")
    
    # Test Case 3: Ambiguous case
    print("\n" + "="*70)
    print("TEST 3: Ambiguous Configuration")
    print("="*70)
    
    test3_code = '''
resource "aws_s3_bucket" "temp_storage" {
  bucket = "temporary-file-uploads"
  acl    = "public-read"
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
'''
    
    test3_features = {
        'public_access': 1,
        'encryption_enabled': 1,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 0,
        'has_tags': 0
    }
    
    result3 = analyzer.analyze(test3_code, "temp_storage", test3_features)
    
    print(f"\n📊 RESULTS:")
    print(f"   Intent: {result3['intent']}")
    print(f"   Purpose: {result3['purpose']}")
    print(f"   LLM Risk Score: {result3['llm_risk_score']:.2f}")
    print(f"   Confidence: {result3['confidence']:.2f}")
    print(f"   Concerns: {', '.join(result3['concerns']) if result3['concerns'] else 'None'}")
    print(f"   Reasoning: {result3['reasoning']}")
    
    print("\n" + "="*70)
    print("  ALL TESTS COMPLETE")
    print("="*70 + "\n")