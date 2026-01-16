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