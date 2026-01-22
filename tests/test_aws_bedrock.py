"""
Test AWS Bedrock Connection
Tests if we can access AWS Bedrock and Claude models
"""

import boto3
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_bedrock_access():
    """
    Test if we can access AWS Bedrock
    Returns True if Bedrock is available, False otherwise
    """
    
    print("\n" + "="*70)
    print("  AWS BEDROCK CONNECTION TEST")
    print("="*70 + "\n")
    
    try:
        # Create Bedrock client
        print("🔌 Attempting to connect to AWS Bedrock...")
        
        bedrock = boto3.client(
            'bedrock',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        print("✅ AWS Bedrock client created successfully\n")
        
        # List available foundation models
        print("📋 Fetching available models...")
        response = bedrock.list_foundation_models()
        
        models = response.get('modelSummaries', [])
        print(f"✅ Found {len(models)} foundation models\n")
        
        # Check for Claude models specifically
        print("🔍 Searching for Claude models...")
        claude_models = [
            model for model in models 
            if 'claude' in model['modelId'].lower()
        ]
        
        if claude_models:
            print(f"✅ Found {len(claude_models)} Claude model(s):\n")
            for model in claude_models:
                print(f"   • {model['modelId']}")
                print(f"     Provider: {model['providerName']}")
                print(f"     Status: {'Available' if model.get('modelLifecycle', {}).get('status') == 'ACTIVE' else 'Pending'}")
                print()
            
            # Test if we can invoke a model
            print("🧪 Testing model invocation...")
            test_invoke_bedrock()
            
            return True
        else:
            print("⚠️  No Claude models found")
            print("   This usually means:")
            print("   1. Bedrock access not yet approved")
            print("   2. Claude models not available in your region")
            print("   3. Need to request model access in AWS Console\n")
            print("📝 ACTION REQUIRED:")
            print("   1. Go to AWS Console → Bedrock → Model Access")
            print("   2. Request access to 'Anthropic - Claude 3 Sonnet'")
            print("   3. Wait for approval (usually 1-3 business days)\n")
            return False
    
    except Exception as e:
        print(f"❌ Error connecting to AWS Bedrock:")
        print(f"   {str(e)}\n")
        
        # Provide helpful error messages
        error_str = str(e).lower()
        
        if 'credentials' in error_str or 'access' in error_str:
            print("💡 TROUBLESHOOTING:")
            print("   • Check AWS credentials in .env file")
            print("   • Run: aws configure")
            print("   • Verify IAM permissions")
        
        elif 'region' in error_str:
            print("💡 TROUBLESHOOTING:")
            print("   • Bedrock may not be available in your region")
            print("   • Try region: us-east-1 or us-west-2")
        
        elif 'not subscribed' in error_str or 'access denied' in error_str:
            print("💡 TROUBLESHOOTING:")
            print("   • Request Bedrock access in AWS Console")
            print("   • Check IAM policy includes bedrock:* permissions")
        
        print()
        return False

def test_invoke_bedrock():
    """
    Test actually calling Bedrock with a simple prompt
    """
    
    try:
        bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Simple test prompt
        test_prompt = "Say hello in exactly 5 words."
        
        print(f"   Sending test prompt: '{test_prompt}'")
        
        # Prepare request body for Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        })
        
        # Call Bedrock
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=body
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        response_text = response_body['content'][0]['text']
        
        print(f"   ✅ Response: {response_text}")
        print("\n🎉 AWS Bedrock is fully functional!")
        
        return True
    
    except Exception as e:
        error_msg = str(e)
        
        if 'access denied' in error_msg.lower():
            print(f"   ⚠️  Cannot invoke model yet")
            print(f"   Reason: Model access pending approval")
        else:
            print(f"   ⚠️  Cannot invoke model: {error_msg}")
        
        return False

def check_openai_fallback():
    """
    Check if OpenAI API is available as fallback
    """
    
    print("\n" + "="*70)
    print("  OPENAI FALLBACK CHECK")
    print("="*70 + "\n")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if openai_key and openai_key.startswith('sk-'):
        print("✅ OpenAI API key found")
        print("   Will use OpenAI as temporary fallback\n")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            print("🧪 Testing OpenAI connection...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Say hello in 5 words"}
                ],
                max_tokens=20
            )
            
            print(f"   ✅ Response: {response.choices[0].message.content}")
            print("\n🎉 OpenAI is working as fallback!")
            return True
        
        except Exception as e:
            print(f"   ❌ OpenAI error: {e}")
            return False
    else:
        print("⚠️  No OpenAI API key found")
        print("   Add OPENAI_API_KEY to .env file for fallback")
        return False

def display_summary():
    """Display test summary and next steps"""
    
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70 + "\n")
    
    bedrock_available = test_bedrock_access()
    openai_available = check_openai_fallback()
    
    print("\n" + "="*70)
    print("  RECOMMENDATION")
    print("="*70 + "\n")
    
    if bedrock_available:
        print("✅ AWS Bedrock is ready to use!")
        print("   Continue with LLM integration using Bedrock\n")
    elif openai_available:
        print("⚠️  Bedrock not available, but OpenAI is working")
        print("   Proceed with OpenAI as temporary fallback")
        print("   Switch to Bedrock when access is approved\n")
    else:
        print("❌ Neither Bedrock nor OpenAI available")
        print("\n📝 ACTION REQUIRED:")
        print("   Option 1: Get AWS Bedrock access")
        print("      • Go to AWS Console → Bedrock → Model Access")
        print("      • Request access to Claude 3 Sonnet")
        print("      • Wait 1-3 business days")
        print()
        print("   Option 2: Get OpenAI API key (faster)")
        print("      • Sign up at platform.openai.com")
        print("      • Create API key")
        print("      • Add to .env: OPENAI_API_KEY=sk-...")
        print()

if __name__ == '__main__':
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        print("   Create .env file with:")
        print("""
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
OPENAI_API_KEY=sk-your_key (optional)
""")
        exit(1)
    
    display_summary()