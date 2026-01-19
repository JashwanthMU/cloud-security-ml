"""
Complete analysis pipeline:
1. Parse Terraform file
2. Extract features
3. ML prediction
4. Generate recommendations
"""

import sys
import os
import tempfile  # ← ADDED THIS
sys.path.append('src')

from ingestion.parse_terraform import parse_terraform_file
from ingestion.extract_features import extract_security_features
from ml_model.test_model import predict_risk

def analyze_terraform(file_path=None, terraform_code=None):
    """
    Complete analysis of Terraform configuration
    
    Args:
        file_path: Path to .tf file OR
        terraform_code: Raw Terraform code as string
    
    Returns:
        Analysis result dictionary
    """
    
    # Step 1: Parse Terraform
    if file_path:
        parsed = parse_terraform_file(file_path)
    elif terraform_code:
        # FIXED: Use system temp directory (works on Windows)
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, 'temp_terraform.tf')
        
        with open(temp_path, 'w') as f:
            f.write(terraform_code)
        
        parsed = parse_terraform_file(temp_path)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
    else:
        return {"error": "No input provided"}
    
    if not parsed or not parsed['resources']:
        return {"error": "No resources found in Terraform code"}
    
    # Analyze each resource
    results = []
    
    for resource in parsed['resources']:
        # Step 2: Extract features
        features = extract_security_features(resource)
        
        # Step 3: ML Prediction
        prediction = predict_risk(features)
        
        # Step 4: Generate human-readable explanation
        explanation = generate_explanation(features, prediction)
        
        # Step 5: Generate fix suggestions
        suggestions = generate_fix_suggestions(resource, features)
        
        result = {
            'resource_type': resource['type'],
            'resource_name': resource['name'],
            'decision': prediction['decision'],
            'risk_score': round(prediction['risk_score'], 2),
            'confidence': round(prediction['confidence'], 2),
            'explanation': explanation,
            'problems': identify_problems(features),
            'suggestions': suggestions,
            'features': features
        }
        
        results.append(result)
    
    # Determine overall risk
    max_risk = max([r['risk_score'] for r in results])
    
    if max_risk > 0.7:
        overall_decision = "BLOCK"
    elif max_risk > 0.3:
        overall_decision = "WARN"
    else:
        overall_decision = "ALLOW"
    
    return {
        'overall_decision': overall_decision,
        'overall_risk_score': round(max_risk, 2),
        'total_resources': len(results),
        'resources': results
    }

def generate_explanation(features, prediction):
    """Generate human-readable explanation"""
    
    decision = prediction['decision']
    risk_score = prediction['risk_score']
    
    if decision == "RISKY":
        explanation = f"This configuration is classified as RISKY with {risk_score:.0%} confidence. "
    else:
        explanation = f"This configuration appears SAFE with {(1-risk_score):.0%} confidence. "
    
    # Add specific reasons
    if features['public_access']:
        explanation += "Public access is enabled. "
    if not features['encryption_enabled']:
        explanation += "Encryption is not enabled. "
    if features['sensitive_naming']:
        explanation += "Resource name suggests sensitive data. "
    
    return explanation

def identify_problems(features):
    """List specific problems found"""
    
    problems = []
    
    if features['public_access']:
        problems.append("🔓 Public access enabled")
    
    if not features['encryption_enabled']:
        problems.append("🔒 No encryption configured")
    
    if not features['versioning_enabled']:
        problems.append("📦 Versioning not enabled")
    
    if not features['logging_enabled']:
        problems.append("📝 Logging not enabled")
    
    if features['sensitive_naming']:
        problems.append("⚠️ Sensitive data naming pattern detected")
    
    if not features['has_tags']:
        problems.append("🏷️ No tags configured")
    
    return problems if problems else ["✅ No obvious problems detected"]

def generate_fix_suggestions(resource, features):
    """Generate actionable fix suggestions"""
    
    suggestions = []
    
    if features['public_access']:
        suggestions.append({
            'problem': 'Public access enabled',
            'fix': 'Change ACL from "public-read" to "private"',
            'code': 'acl = "private"'
        })
    
    if not features['encryption_enabled']:
        suggestions.append({
            'problem': 'No encryption',
            'fix': 'Enable server-side encryption',
            'code': '''server_side_encryption_configuration {
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}'''
        })
    
    if not features['versioning_enabled']:
        suggestions.append({
            'problem': 'No versioning',
            'fix': 'Enable versioning for data protection',
            'code': '''versioning {
  enabled = true
}'''
        })
    
    return suggestions if suggestions else [
        {'problem': 'None', 'fix': 'Configuration looks good!', 'code': ''}
    ]

# Test the complete pipeline
if __name__ == '__main__':
    
    # Test with risky Terraform code
    test_code = '''
resource "aws_s3_bucket" "customer_data" {
  bucket = "my-customer-database-backup"
  acl    = "public-read"
}
'''
    
    print("🔍 Analyzing Terraform configuration...\n")
    result = analyze_terraform(terraform_code=test_code)
    
    import json
    print(json.dumps(result, indent=2))