"""
Week 1 Model Performance Analysis
Detailed analysis of the Random Forest model trained in Week 1
Generates visualizations and identifies areas for improvement
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, 
    classification_report,
    roc_curve,
    roc_auc_score,
    precision_recall_curve
)
import os

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class Week1ModelAnalyzer:
    """
    Comprehensive analysis of Week 1 ML model
    """
    
    def __init__(self):
        self.model = None
        self.dataset = None
        self.X = None
        self.y = None
        self.feature_columns = [
            'public_access',
            'encryption_enabled',
            'versioning_enabled',
            'logging_enabled',
            'sensitive_naming',
            'has_tags'
        ]
    
    def load_data(self):
        """Load trained model and dataset"""
        
        print("="*70)
        print("  WEEK 1 MODEL ANALYSIS")
        print("="*70)
        print()
        
        # Load model
        print("📦 Loading trained model...")
        try:
            self.model = joblib.load('models/random_forest_v1.pkl')
            print("   ✅ Model loaded: Random Forest")
        except FileNotFoundError:
            print("   ❌ Error: models/random_forest_v1.pkl not found")
            print("   Run: python src/ml_model/train_model.py first")
            return False
        
        # Load dataset
        print("\n📊 Loading dataset...")
        try:
            self.dataset = pd.read_csv('data/processed/dataset.csv')
            print(f"   ✅ Dataset loaded: {len(self.dataset)} examples")
        except FileNotFoundError:
            print("   ❌ Error: data/processed/dataset.csv not found")
            print("   Run: python src/ingestion/process_all_files.py first")
            return False
        
        # Prepare features and labels
        self.X = self.dataset[self.feature_columns]
        self.y = self.dataset['label']
        
        print(f"   Features: {len(self.feature_columns)}")
        print(f"   Safe examples: {sum(self.y == 0)}")
        print(f"   Risky examples: {sum(self.y == 1)}")
        
        return True
    
    def analyze_performance(self):
        """Generate performance metrics"""
        
        print("\n" + "="*70)
        print("  PERFORMANCE METRICS")
        print("="*70)
        
        # Make predictions
        y_pred = self.model.predict(self.X)
        y_pred_proba = self.model.predict_proba(self.X)[:, 1]
        
        # Accuracy
        accuracy = (y_pred == self.y).mean()
        print(f"\n📈 Overall Accuracy: {accuracy:.2%}")
        
        # Detailed classification report
        print("\n📊 Classification Report:")
        print("-" * 70)
        report = classification_report(
            self.y, 
            y_pred, 
            target_names=['SAFE', 'RISKY'],
            digits=3
        )
        print(report)
        
        # Confusion Matrix
        cm = confusion_matrix(self.y, y_pred)
        
        print("\n🔢 Confusion Matrix:")
        print("-" * 70)
        print(f"                  Predicted")
        print(f"                SAFE    RISKY")
        print(f"Actual  SAFE    {cm[0][0]:4d}    {cm[0][1]:4d}")
        print(f"        RISKY   {cm[1][0]:4d}    {cm[1][1]:4d}")
        
        # ROC-AUC Score
        roc_auc = roc_auc_score(self.y, y_pred_proba)
        print(f"\n🎯 ROC-AUC Score: {roc_auc:.3f}")
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': cm,
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'roc_auc': roc_auc
        }
    
    def visualize_confusion_matrix(self, cm):
        """Create confusion matrix heatmap"""
        
        print("\n📊 Generating confusion matrix visualization...")
        
        plt.figure(figsize=(8, 6))
        
        # Create heatmap
        sns.heatmap(
            cm, 
            annot=True, 
            fmt='d', 
            cmap='Blues',
            xticklabels=['SAFE', 'RISKY'],
            yticklabels=['SAFE', 'RISKY'],
            cbar_kws={'label': 'Count'}
        )
        
        plt.title('Confusion Matrix - Week 1 Model\n', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        
        # Add accuracy text
        accuracy = (cm[0][0] + cm[1][1]) / cm.sum()
        plt.text(
            1, -0.15, 
            f'Overall Accuracy: {accuracy:.2%}',
            ha='center',
            transform=plt.gca().transAxes,
            fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        plt.tight_layout()
        plt.savefig('analysis/confusion_matrix_week1.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved: analysis/confusion_matrix_week1.png")
        
        plt.close()
    
    def visualize_feature_importance(self):
        """Create feature importance chart"""
        
        print("\n📊 Generating feature importance visualization...")
        
        # Get feature importances
        importances = self.model.feature_importances_
        
        # Create DataFrame
        feature_importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': importances
        }).sort_values('importance', ascending=True)
        
        # Create horizontal bar chart
        plt.figure(figsize=(10, 6))
        
        bars = plt.barh(
            feature_importance_df['feature'],
            feature_importance_df['importance'],
            color=plt.cm.viridis(feature_importance_df['importance'] / importances.max())
        )
        
        plt.xlabel('Importance Score', fontsize=12)
        plt.ylabel('Feature', fontsize=12)
        plt.title('Feature Importance - Week 1 Model\n', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(
                width + 0.01,
                bar.get_y() + bar.get_height()/2,
                f'{width:.3f}',
                va='center',
                fontsize=10
            )
        
        plt.tight_layout()
        plt.savefig('analysis/feature_importance_week1.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved: analysis/feature_importance_week1.png")
        
        plt.close()
        
        return feature_importance_df
    
    def visualize_roc_curve(self, y_true, y_pred_proba, roc_auc):
        """Create ROC curve"""
        
        print("\n📊 Generating ROC curve...")
        
        # Calculate ROC curve
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        
        # Plot ROC curve
        plt.plot(
            fpr, tpr, 
            color='darkorange', 
            lw=2, 
            label=f'ROC curve (AUC = {roc_auc:.3f})'
        )
        
        # Plot diagonal (random classifier)
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random Classifier')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title('ROC Curve - Week 1 Model\n', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('analysis/roc_curve_week1.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved: analysis/roc_curve_week1.png")
        
        plt.close()
    
    def analyze_errors(self, y_true, y_pred):
        """Analyze misclassified examples"""
        
        print("\n" + "="*70)
        print("  ERROR ANALYSIS")
        print("="*70)
        
        # Find errors
        errors = self.dataset[y_true != y_pred].copy()
        errors['predicted'] = y_pred[y_true != y_pred]
        errors['true_label'] = y_true[y_true != y_pred]
        
        print(f"\n❌ Total Errors: {len(errors)} out of {len(self.dataset)}")
        print(f"   Error Rate: {len(errors)/len(self.dataset):.2%}")
        
        if len(errors) == 0:
            print("\n🎉 Perfect accuracy! No errors to analyze.")
            return errors
        
        # False Positives (predicted RISKY, actually SAFE)
        false_positives = errors[errors['true_label'] == 0]
        print(f"\n🔴 False Positives: {len(false_positives)}")
        print("   (Safe configs incorrectly flagged as risky)")
        
        if len(false_positives) > 0:
            print("\n   Examples:")
            for idx, row in false_positives.head(3).iterrows():
                print(f"\n   File: {row['filename']}")
                print(f"   True: SAFE, Predicted: RISKY")
                print(f"   Features: public={row['public_access']}, "
                      f"encrypt={row['encryption_enabled']}, "
                      f"sensitive_name={row['sensitive_naming']}")
        
        # False Negatives (predicted SAFE, actually RISKY)
        false_negatives = errors[errors['true_label'] == 1]
        print(f"\n🔵 False Negatives: {len(false_negatives)}")
        print("   (Risky configs that slipped through)")
        
        if len(false_negatives) > 0:
            print("\n   Examples:")
            for idx, row in false_negatives.head(3).iterrows():
                print(f"\n   File: {row['filename']}")
                print(f"   True: RISKY, Predicted: SAFE")
                print(f"   Features: public={row['public_access']}, "
                      f"encrypt={row['encryption_enabled']}, "
                      f"sensitive_name={row['sensitive_naming']}")
        
        # Save errors to CSV
        errors.to_csv('analysis/misclassified_examples.csv', index=False)
        print(f"\n💾 Saved error details to: analysis/misclassified_examples.csv")
        
        return errors
    
    def generate_improvement_recommendations(self, feature_importance_df, errors):
        """Generate recommendations for Week 2"""
        
        print("\n" + "="*70)
        print("  RECOMMENDATIONS FOR WEEK 2")
        print("="*70)
        
        recommendations = []
        
        # Check feature importance
        low_importance_features = feature_importance_df[
            feature_importance_df['importance'] < 0.1
        ]
        
        if len(low_importance_features) > 0:
            print("\n📉 Low-Impact Features:")
            for _, row in low_importance_features.iterrows():
                print(f"   • {row['feature']}: {row['importance']:.3f}")
            recommendations.append(
                "Consider adding more discriminative features to replace low-impact ones"
            )
        
        # Check error patterns
        if len(errors) > 0:
            print("\n🔍 Error Patterns:")
            
            # Check if errors have common features
            error_features = errors[self.feature_columns]
            feature_means = error_features.mean()
            
            print("\n   Feature values in misclassified examples:")
            for feature, mean_val in feature_means.items():
                print(f"   • {feature}: {mean_val:.2f} (avg)")
            
            recommendations.append(
                "Focus on edge cases where current features are ambiguous"
            )
        
        # Specific recommendations
        print("\n💡 Specific Improvements:")
        
        print("\n   1. Add More Features (Target: 10 features)")
        print("      • MFA delete protection")
        print("      • Lifecycle policies")
        print("      • CORS configuration")
        print("      • Tag quality score")
        
        print("\n   2. Upgrade Model")
        print("      • Try XGBoost (often better than Random Forest)")
        print("      • Experiment with hyperparameter tuning")
        print("      • Consider ensemble methods")
        
        print("\n   3. Collect More Data")
        print("      • Current: 100 examples")
        print("      • Target: 150-200 examples")
        print("      • Focus on edge cases and errors")
        
        print("\n   4. Add LLM Context")
        print("      • Use AI to understand intent")
        print("      • Distinguish intentional vs accidental configs")
        print("      • Target accuracy: 98-99%")
        
        # Save recommendations
        with open('analysis/improvement_plan.md', 'w') as f:
            f.write("# Week 1 Model - Improvement Plan\n\n")
            f.write("## Current Performance\n\n")
            f.write(f"- Accuracy: {(len(self.dataset) - len(errors))/len(self.dataset):.2%}\n")
            f.write(f"- Total Examples: {len(self.dataset)}\n")
            f.write(f"- Errors: {len(errors)}\n\n")
            
            f.write("## Proposed Improvements\n\n")
            f.write("### 1. Feature Engineering\n")
            f.write("Add 4 new features:\n")
            f.write("- MFA delete enabled\n")
            f.write("- Lifecycle policy present\n")
            f.write("- Risky CORS configuration\n")
            f.write("- Tag quality score\n\n")
            
            f.write("### 2. Model Upgrade\n")
            f.write("- Switch from Random Forest to XGBoost\n")
            f.write("- Hyperparameter tuning with GridSearchCV\n")
            f.write("- Target accuracy: 98%+\n\n")
            
            f.write("### 3. Data Collection\n")
            f.write("- Collect 50 more examples (total: 150)\n")
            f.write("- Focus on edge cases\n\n")
            
            f.write("### 4. LLM Integration\n")
            f.write("- Add Claude/GPT for context understanding\n")
            f.write("- Hybrid ML + LLM system\n")
            f.write("- Target accuracy: 99%\n")
        
        print("\n💾 Saved improvement plan to: analysis/improvement_plan.md")
    
    def generate_summary_report(self, metrics):
        """Generate text summary report"""
        
        print("\n" + "="*70)
        print("  GENERATING SUMMARY REPORT")
        print("="*70)
        
        cm = metrics['confusion_matrix']
        accuracy = metrics['accuracy']
        roc_auc = metrics['roc_auc']
        
        # Calculate detailed metrics
        tn, fp, fn, tp = cm.ravel()
        
        precision_safe = tn / (tn + fn) if (tn + fn) > 0 else 0
        recall_safe = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        precision_risky = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall_risky = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        report = f"""
# Week 1 Model Analysis Report

## Model Information
- **Model Type**: Random Forest Classifier
- **Training Date**: Week 1
- **Features**: {len(self.feature_columns)}
- **Dataset Size**: {len(self.dataset)} examples

## Performance Metrics

### Overall Performance
- **Accuracy**: {accuracy:.2%}
- **ROC-AUC Score**: {roc_auc:.3f}

### Confusion Matrix
```
                Predicted
              SAFE   RISKY
Actual SAFE   {tn:4d}   {fp:4d}
       RISKY  {fn:4d}   {tp:4d}
```

### Class-Specific Metrics

**SAFE Class:**
- Precision: {precision_safe:.2%}
- Recall: {recall_safe:.2%}

**RISKY Class:**
- Precision: {precision_risky:.2%}
- Recall: {recall_risky:.2%}

### Error Analysis
- **Total Errors**: {fp + fn}
- **False Positives**: {fp} (Safe configs flagged as risky)
- **False Negatives**: {fn} (Risky configs missed)

## Feature Importance
{self._format_feature_importance()}

## Recommendations for Week 2
1. Add 4 new features (target: 10 total)
2. Upgrade to XGBoost
3. Collect 50 more examples
4. Integrate LLM for context
5. Target accuracy: 98-99%

## Files Generated
- confusion_matrix_week1.png
- feature_importance_week1.png
- roc_curve_week1.png
- misclassified_examples.csv
- improvement_plan.md
"""
        
        # Save report
        with open('analysis/week1_analysis_report.md', 'w') as f:
            f.write(report)
        
        print("\n💾 Saved comprehensive report to: analysis/week1_analysis_report.md")
    
    def _format_feature_importance(self):
        """Helper to format feature importance"""
        
        importances = self.model.feature_importances_
        
        lines = []
        for feature, importance in zip(self.feature_columns, importances):
            lines.append(f"- {feature}: {importance:.3f}")
        
        return "\n".join(lines)
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        
        # Load data
        if not self.load_data():
            return
        
        # Analyze performance
        metrics = self.analyze_performance()
        
        # Generate visualizations
        self.visualize_confusion_matrix(metrics['confusion_matrix'])
        feature_importance_df = self.visualize_feature_importance()
        self.visualize_roc_curve(self.y, metrics['probabilities'], metrics['roc_auc'])
        
        # Error analysis
        errors = self.analyze_errors(self.y, metrics['predictions'])
        
        # Recommendations
        self.generate_improvement_recommendations(feature_importance_df, errors)
        
        # Summary report
        self.generate_summary_report(metrics)
        
        print("\n" + "="*70)
        print("  ANALYSIS COMPLETE")
        print("="*70)
        print("\n📁 All files saved to: analysis/")
        print("\n   Generated files:")
        print("   • confusion_matrix_week1.png")
        print("   • feature_importance_week1.png")
        print("   • roc_curve_week1.png")
        print("   • misclassified_examples.csv")
        print("   • improvement_plan.md")
        print("   • week1_analysis_report.md")
        print("\n✅ Week 1 model analysis complete!\n")

# Main execution
if __name__ == '__main__':
    # Create analyzer
    analyzer = Week1ModelAnalyzer()
    
    # Run full analysis
    analyzer.run_full_analysis()