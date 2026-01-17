import os
import pandas as pd
from parse_terraform import parse_terraform_file
from extract_features import extract_security_features

def process_all_files(data_dir='data/raw'):
    """
    Process all Terraform files and create dataset
    """
    
    all_data = []
    
    # Get all .tf files
    categories = ['safe', 'risky', 'unsure']
    
    for category in categories:
        category_dir = os.path.join(data_dir, category)
        
        if not os.path.exists(category_dir):
            print(f"Directory {category_dir} not found, skipping...")
            continue
        
        # Get all .tf files in this category
        files = [f for f in os.listdir(category_dir) if f.endswith('.tf')]
        
        print(f"Processing {len(files)} files from {category}...")
        
        for filename in files:
            file_path = os.path.join(category_dir, filename)
            
            # Parse file
            parsed = parse_terraform_file(file_path)
            
            if not parsed or not parsed['resources']:
                print(f"  ⚠️  Skipping {filename} - no resources found")
                continue
            
            # Process each resource
            for resource in parsed['resources']:
                # Extract features
                features = extract_security_features(resource)
                
                # Add metadata
                features['filename'] = filename
                features['category'] = category
                features['resource_type'] = resource['type']
                features['resource_name'] = resource['name']
                
                # Add label (for machine learning)
                # SAFE = 0, RISKY = 1
                features['label'] = 0 if category == 'safe' else 1
                
                all_data.append(features)
            
            print(f"  ✅ Processed {filename}")
    
    # Convert to pandas DataFrame (like Excel spreadsheet)
    df = pd.DataFrame(all_data)
    
    # Save to CSV
    output_path = 'data/processed/dataset.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Dataset created: {output_path}")
    print(f"   Total examples: {len(df)}")
    print(f"   Safe: {len(df[df['label']==0])}")
    print(f"   Risky: {len(df[df['label']==1])}")
    
    return df

if __name__ == '__main__':
    dataset = process_all_files()
    
    # Show first few rows
    print("\nFirst 5 examples:")
    print(dataset.head())