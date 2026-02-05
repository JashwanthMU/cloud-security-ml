"""
Script to collect Terraform files from GitHub
"""

import requests
import os
import time
import base64

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Optional: Get from GitHub Settings → Tokens

def search_terraform_files(query, max_results=50):
    """
    Search GitHub for Terraform files
    
    Args:
        query: Search query (e.g., "resource aws_s3_bucket")
        max_results: Maximum files to collect
    """
    
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    url = 'https://api.github.com/search/code'
    params = {
        'q': f'{query} language:HCL',
        'per_page': 30
    }
    
    print(f"Searching for: {query}")
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []
    
    results = response.json()
    items = results.get('items', [])
    
    files_content = []
    
    for item in items[:max_results]:
        try:
            # Get file content
            content_url = item['url']
            content_response = requests.get(content_url, headers=headers)
            
            if content_response.status_code == 200:
                content_data = content_response.json()
                
                # Decode base64 content
                encoded_content = content_data.get('content', '')
                decoded = base64.b64decode(encoded_content).decode('utf-8')
                
                files_content.append({
                    'filename': item['name'],
                    'repo': item['repository']['full_name'],
                    'content': decoded
                })
                
                print(f"✅ Collected: {item['name']} from {item['repository']['full_name']}")
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error with {item['name']}: {e}")
            continue
    
    return files_content

def save_files(files, category='safe'):
    """Save collected files"""
    
    os.makedirs(f'data/raw/{category}', exist_ok=True)
    
    for i, file_data in enumerate(files):
        filename = f"github_{category}_{i+1:03d}.tf"
        filepath = f"data/raw/{category}/{filename}"
        
        with open(filepath, 'w') as f:
            f.write(file_data['content'])
        
        print(f"Saved: {filepath}")

if __name__ == '__main__':
    
    print("=" * 60)
    print("Collecting SAFE configurations...")
    print("=" * 60)
    
    # Safe patterns
    safe_queries = [
        'resource aws_s3_bucket acl private encryption',
        'resource aws_rds_instance encrypted storage_encrypted true',
        'resource aws_security_group ingress specific'
    ]
    
    all_safe = []
    for query in safe_queries:
        files = search_terraform_files(query, max_results=30)
        all_safe.extend(files)
        time.sleep(5)  # Avoid rate limiting
    
    save_files(all_safe[:100], 'safe')
    
    print("\n" + "=" * 60)
    print("Collecting RISKY configurations...")
    print("=" * 60)
    
    # Risky patterns
    risky_queries = [
        'resource aws_s3_bucket acl public-read',
        'resource aws_security_group ingress 0.0.0.0/0',
        'resource aws_db_instance publicly_accessible true'
    ]
    
    all_risky = []
    for query in risky_queries:
        files = search_terraform_files(query, max_results=30)
        all_risky.extend(files)
        time.sleep(5)
    
    save_files(all_risky[:100], 'risky')
    
    print("\n" + "=" * 60)
    print("Collection Complete!")
    print(f"Safe files: {len(all_safe[:100])}")
    print(f"Risky files: {len(all_risky[:100])}")
    print("=" * 60)