import joblib
import pandas as pd

def predict_risk(features):
    """
    Use trained model to predict risk
    
    Args:
        features: Dictionary with feature values
    
    Returns:
        prediction and risk score
    """
    
    # Load trained model
    model = joblib.load('models/random_forest_v1.pkl')
    
    # Convert features to DataFrame (model expects this format)
    feature_columns = [
        'public_access',
        'encryption_enabled',
        'versioning_enabled',
        'logging_enabled',
        'sensitive_naming',
        'has_tags'
    ]
    
    # Create DataFrame with one row
    X = pd.DataFrame([features], columns=feature_columns)
    
    # Predict
    prediction = model.predict(X)[0]  # 0 or 1
    probability = model.predict_proba(X)[0]  # [prob_safe, prob_risky]
    
    risk_score = probability[1]  # Probability of being risky
    
    decision = "RISKY" if prediction == 1 else "SAFE"
    
    return {
        'decision': decision,
        'risk_score': risk_score,
        'confidence': max(probability)
    }

# Test with examples
if __name__ == '__main__':
    
    # Test Case 1: Safe configuration
    print("Test Case 1: Safe Configuration")
    safe_config = {
        'public_access': 0,
        'encryption_enabled': 1,
        'versioning_enabled': 1,
        'logging_enabled': 1,
        'sensitive_naming': 0,
        'has_tags': 1
    }
    result = predict_risk(safe_config)
    print(f"  Decision: {result['decision']}")
    print(f"  Risk Score: {result['risk_score']:.2f}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print()
    
    # Test Case 2: Risky configuration
    print("Test Case 2: Risky Configuration")
    risky_config = {
        'public_access': 1,
        'encryption_enabled': 0,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 1,
        'has_tags': 0
    }
    result = predict_risk(risky_config)
    print(f"  Decision: {result['decision']}")
    print(f"  Risk Score: {result['risk_score']:.2f}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print()
    
    # Test Case 3: Medium risk
    print("Test Case 3: Medium Risk Configuration")
    medium_config = {
        'public_access': 1,
        'encryption_enabled': 1,
        'versioning_enabled': 0,
        'logging_enabled': 0,
        'sensitive_naming': 0,
        'has_tags': 1
    }
    result = predict_risk(medium_config)
    print(f"  Decision: {result['decision']}")
    print(f"  Risk Score: {result['risk_score']:.2f}")
    print(f"  Confidence: {result['confidence']:.2f}")