"""
Verify collected dataset
"""

import os
import glob

def verify_dataset():
    print("🔍 Verifying dataset...\n")
    
    # Count files
    safe_files = glob.glob('data/raw/safe/*.tf')
    risky_files = glob.glob('data/raw/risky/*.tf')
    
    print(f"📊 File Counts:")
    print(f"   Safe: {len(safe_files)}")
    print(f"   Risky: {len(risky_files)}")
    print(f"   Total: {len(safe_files) + len(risky_files)}")
    
    # Check CSV
    if os.path.exists('data/labels.csv'):
        with open('data/labels.csv', 'r') as f:
            lines = f.readlines()
        print(f"\n📋 labels.csv: {len(lines)-1} entries")
    
    # Sample content
    print(f"\n📄 Sample safe file:")
    if safe_files:
        with open(safe_files[0], 'r') as f:
            print(f.read()[:200] + "...")
    
    print(f"\n⚠️  Sample risky file:")
    if risky_files:
        with open(risky_files[0], 'r') as f:
            print(f.read()[:200] + "...")
    
    # Status
    if len(safe_files) >= 50 and len(risky_files) >= 50:
        print(f"\n✅ Dataset is complete and ready!")
    else:
        print(f"\n⚠️  Need more files:")
        print(f"   Safe: {50 - len(safe_files)} more needed")
        print(f"   Risky: {50 - len(risky_files)} more needed")

if __name__ == '__main__':
    verify_dataset()