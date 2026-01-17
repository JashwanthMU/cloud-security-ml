import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_model():
    """
    Train machine learning model to classify configurations
    """
    
    print("📊 Loading dataset...")
    df = pd.read_csv('data/processed/dataset.csv')
    
    # Select features for training
    feature_columns = [
        'public_access',
        'encryption_enabled',
        'versioning_enabled',
        'logging_enabled',
        'sensitive_naming',
        'has_tags'
    ]
    
    X = df[feature_columns]  # Features (input)
    y = df['label']          # Label (output: 0=safe, 1=risky)
    
    print(f"   Total examples: {len(df)}")
    print(f"   Features: {len(feature_columns)}")
    
    # Split into training (80%) and testing (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Continue from train_model.py

    print(f"\n🔨 Training model...")
    print(f"   Training examples: {len(X_train)}")
    print(f"   Testing examples: {len(X_test)}")
    
    # Create Random Forest model (simple but powerful)
    model = RandomForestClassifier(
        n_estimators=100,      # 100 decision trees
        max_depth=5,           # Not too deep (avoid overfitting)
        random_state=42        # For reproducibility
    )
    
    # Train the model
    model.fit(X_train, y_train)
    
    print("✅ Model trained!")
    
    # Test the model
    print("\n📈 Testing model...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Accuracy: {accuracy:.2%}")
    
    # Detailed report
    print("\n📊 Detailed Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['SAFE', 'RISKY']))
    
    # Feature importance (what matters most?)
    print("\n🔍 Feature Importance:")
    for feature, importance in zip(feature_columns, model.feature_importances_):
        print(f"   {feature}: {importance:.3f}")
    
    # Save the model
    model_path = 'models/random_forest_v1.pkl'
    joblib.dump(model, model_path)
    print(f"\n💾 Model saved: {model_path}")
    
    return model

if __name__ == '__main__':
    model = train_model()