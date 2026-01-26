def extract_security_features(resource):
    """
    Extracts security-relevant features from a resource
    
    Args:
        resource: Parsed resource dictionary
        
    Returns:
        Dictionary of features
    """
    
    properties = resource['properties']
    features = {}
    
    # Feature 1: Public access
    acl = properties.get('acl', 'private')
    features['public_access'] = 1 if 'public' in acl else 0
    
    # Feature 2: Encryption
    has_encryption = 'server_side_encryption_configuration' in properties
    features['encryption_enabled'] = 1 if has_encryption else 0
    
    # Feature 3: Versioning
    versioning = properties.get('versioning', {})

    # FIX list case
    if isinstance(versioning, list) and len(versioning) > 0:
        versioning = versioning[0]

    features['versioning_enabled'] = 1 if versioning.get('enabled') else 0

    
    # Feature 4: Logging
    logging = properties.get('logging', {})

    if isinstance(logging, list) and len(logging) > 0:
        logging = logging[0]

    features['logging_enabled'] = 1 if logging else 0

    
    # Feature 5: Sensitive naming
    bucket_name = properties.get('bucket', '')
    sensitive_keywords = ['customer', 'user', 'personal', 'data', 'backup', 'prod']
    features['sensitive_naming'] = 1 if any(kw in bucket_name.lower() for kw in sensitive_keywords) else 0
    
    # Feature 6: Tags present
    tags = properties.get('tags', {})
    features['has_tags'] = 1 if tags else 0
    
def extract_security_features(resource):
    """
    Extract 10 security features (upgraded from 6)
    """
    
    properties = resource['properties']
    features = {}
    
    # ORIGINAL 6 FEATURES
    acl = properties.get('acl', 'private')
    features['public_access'] = 1 if 'public' in acl else 0
    
    has_encryption = 'server_side_encryption_configuration' in properties
    features['encryption_enabled'] = 1 if has_encryption else 0
    
    versioning = properties.get('versioning', {})
    features['versioning_enabled'] = 1 if versioning.get('enabled') else 0
    
    logging = properties.get('logging', {})
    features['logging_enabled'] = 1 if logging else 0
    
    bucket_name = properties.get('bucket', '')
    sensitive_keywords = ['customer', 'user', 'personal', 'data', 'backup', 'prod']
    features['sensitive_naming'] = 1 if any(kw in bucket_name.lower() for kw in sensitive_keywords) else 0
    
    tags = properties.get('tags', {})
    features['has_tags'] = 1 if tags else 0
    
    # NEW FEATURE 7: MFA Delete
    mfa_delete = versioning.get('mfa_delete', False)
    features['mfa_delete_enabled'] = 1 if mfa_delete else 0
    
    # NEW FEATURE 8: Lifecycle Policy
    lifecycle = properties.get('lifecycle_rule', [])
    features['has_lifecycle_policy'] = 1 if lifecycle else 0
    
    # NEW FEATURE 9: Risky CORS
    cors = properties.get('cors_rule', [])
    if cors:
        has_wildcard_cors = any(
            '*' in rule.get('allowed_origins', []) 
            for rule in (cors if isinstance(cors, list) else [cors])
        )
        features['risky_cors'] = 1 if has_wildcard_cors else 0
    else:
        features['risky_cors'] = 0
    
    # NEW FEATURE 10: Tag Quality
    if tags:
        required_tags = ['Environment', 'Owner', 'Purpose']
        tag_quality = sum(1 for tag in required_tags if tag in tags)
        features['tag_quality'] = tag_quality / len(required_tags)
    else:
        features['tag_quality'] = 0.0
    
    return features

# Test
if __name__ == '__main__':
    from parse_terraform import parse_terraform_file
    
    # Parse file
    parsed = parse_terraform_file('data/raw/safe/example_001.tf')
    
    # Extract features from first resource
    if parsed and parsed['resources']:
        resource = parsed['resources'][0]
        features = extract_security_features(resource)
        
        print("Extracted Features:")
        for key, value in features.items():
            print(f"  {key}: {value}")