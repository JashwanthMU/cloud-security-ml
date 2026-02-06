"""
Hybrid Analyzer - Combines ML + LLM
Week 2 Innovation
"""

import sys
sys.path.append('src')

from ingestion.parse_terraform import parse_terraform_file
from ingestion.extract_features import extract_security_features
from ml_model.test_model import predict_risk
from llm.llm_analyzer import LLMAnalyzer

class HybridAnalyzer:
    """Combines ML pattern matching with LLM context understanding"""
    
    def __init__(self):
        self.llm = LLMAnalyzer()
        self.version = "2.0"
    
    def analyze(self, terraform_code):
        """Complete hybrid analysis"""
        
        # Parse
        temp_path = '/tmp/analysis.tf'
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(terraform_code)
        
        parsed = parse_terraform_file(temp_path)
        if not parsed or not parsed['resources']:
            return {"error": "No resources found"}
        
        resource = parsed['resources'][0]
        features = extract_security_features(resource)
        
        # ML prediction
        ml_result = predict_risk(features)
        ml_score = ml_result['risk_score']
        
        # LLM analysis
        llm_result = self.llm.analyze_intent(
            terraform_code,
            resource['name'],
            features
        )
        llm_score = llm_result['llm_risk_score']
        
        # Fusion
        final_score = self._fuse_scores(ml_score, llm_score, llm_result)
        decision = self._make_decision(final_score, llm_result['intent'])
        
        return {
            'version': self.version,
            'decision': decision,
            'risk_score': round(final_score, 2),
            'ml_score': round(ml_score, 2),
            'llm_score': round(llm_score, 2),
            'intent': llm_result['intent'],
            'reasoning': llm_result['reasoning'],
            'concerns': llm_result.get('concerns', []),
            'problems': self._list_problems(features),
            'resource': {
                'type': resource['type'],
                'name': resource['name']
            }
        }
    
    def _fuse_scores(self, ml_score, llm_score, llm_result):
        """Intelligent fusion algorithm"""
        
        intent = llm_result['intent']
        
        # Adjust weights based on intent
        if intent == 'INTENTIONAL':
            weight_ml, weight_llm = 0.4, 0.6
        elif intent == 'ACCIDENTAL':
            weight_ml, weight_llm = 0.7, 0.3
        else:
            weight_ml, weight_llm = 0.6, 0.4
        
        return (ml_score * weight_ml) + (llm_score * weight_llm)
    
    def _make_decision(self, score, intent):
        """Decision logic"""
        
        if score > 0.75:
            return "BLOCK"
        elif score > 0.45:
            return "BLOCK" if intent == "ACCIDENTAL" else "WARN"
        elif score > 0.25:
            return "WARN"
        else:
            return "ALLOW"
    
    def _list_problems(self, features):
        """List identified problems"""
        
        problems = []
        if features.get('public_access'):
            problems.append("🔓 Public access enabled")
        if not features.get('encryption_enabled'):
            problems.append("🔒 No encryption")
        if features.get('sensitive_naming'):
            problems.append("⚠️ Sensitive naming pattern")
        
        return problems if problems else ["✅ No major issues"]

# Test
if __name__ == '__main__':
    analyzer = HybridAnalyzer()
    
    test = '''
resource "aws_s3_bucket" "data" {
  bucket = "customer-data"
  acl    = "public-read"
}
'''
    
    result = analyzer.analyze(test)
    
    print(f"Decision: {result['decision']}")
    print(f"Score: {result['risk_score']}")
    print(f"Intent: {result['intent']}")
    print(f"Reasoning: {result['reasoning']}")