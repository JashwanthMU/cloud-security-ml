"""
LLM Wrapper - Universal interface for Large Language Models
Supports both AWS Bedrock (Claude) and OpenAI (GPT)
Automatically detects which provider is available
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMWrapper:
    """
    Unified interface for LLM calls
    Automatically uses best available provider:
    1. AWS Bedrock (Claude 3) - preferred for production
    2. OpenAI (GPT-3.5) - fallback for development
    """
    
    def __init__(self, verbose=False):
        """
        Initialize LLM wrapper
        
        Args:
            verbose: If True, print detailed logs
        """
        self.verbose = verbose
        self.provider = None
        self.client = None
        self.model_id = None
        
        # Try to initialize provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """
        Detect and initialize available LLM provider
        Priority: Bedrock > OpenAI
        """
        
        # Try AWS Bedrock first
        if self._try_bedrock():
            self.provider = 'bedrock'
            if self.verbose:
                print("✅ Using AWS Bedrock (Claude 3 Sonnet)")
            return
        
        # Fallback to OpenAI
        if self._try_openai():
            self.provider = 'openai'
            if self.verbose:
                print("✅ Using OpenAI (GPT-3.5 Turbo)")
            return
        
        # No provider available
        raise ValueError(
            "No LLM provider available. Please configure either:\n"
            "1. AWS Bedrock: Set AWS credentials and request model access\n"
            "2. OpenAI: Set OPENAI_API_KEY in .env file"
        )
    
    def _try_bedrock(self):
        """Try to initialize AWS Bedrock"""
        
        try:
            # Check if credentials exist
            if not os.getenv('AWS_ACCESS_KEY_ID'):
                if self.verbose:
                    print("⏭️  Skipping Bedrock (no AWS credentials)")
                return False
            
            import boto3
            
            # Create Bedrock runtime client
            self.client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # Set model ID
            self.model_id = os.getenv(
                'AWS_BEDROCK_MODEL',
                'anthropic.claude-3-sonnet-20240229-v1:0'
            )
            
            # Test with a simple call
            test_body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hello"}]
            })
            
            self.client.invoke_model(
                modelId=self.model_id,
                body=test_body
            )
            
            return True
        
        except Exception as e:
            if self.verbose:
                print(f"⏭️  Skipping Bedrock: {str(e)[:50]}...")
            return False
    
    def _try_openai(self):
        """Try to initialize OpenAI"""
        
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                if self.verbose:
                    print("⏭️  Skipping OpenAI (no API key)")
                return False
            
            from openai import OpenAI
            
            self.client = OpenAI(api_key=api_key)
            self.model_id = "gpt-3.5-turbo"
            
            # Test with a simple call
            self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return True
        
        except Exception as e:
            if self.verbose:
                print(f"⏭️  Skipping OpenAI: {str(e)[:50]}...")
            return False
    
    def generate(self, prompt, max_tokens=500, temperature=0.1):
        """
        Generate text using available LLM
        
        Args:
            prompt: Input text prompt
            max_tokens: Maximum length of response
            temperature: Creativity (0.0 = deterministic, 1.0 = creative)
        
        Returns:
            Generated text string
        """
        
        if self.provider == 'bedrock':
            return self._generate_bedrock(prompt, max_tokens, temperature)
        elif self.provider == 'openai':
            return self._generate_openai(prompt, max_tokens, temperature)
        else:
            raise ValueError("No LLM provider initialized")
    
    def _generate_bedrock(self, prompt, max_tokens, temperature):
        """Generate using AWS Bedrock (Claude)"""
        
        try:
            # Prepare request body
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            # Call Bedrock
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text
            text = response_body['content'][0]['text']
            
            return text
        
        except Exception as e:
            raise Exception(f"Bedrock API error: {str(e)}")
    
    def _generate_openai(self, prompt, max_tokens, temperature):
        """Generate using OpenAI (GPT)"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful cloud security expert."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def get_provider_info(self):
        """Get information about current provider"""
        
        return {
            'provider': self.provider,
            'model': self.model_id,
            'available': self.provider is not None
        }

# Test the wrapper
if __name__ == '__main__':
    print("\n" + "="*70)
    print("  LLM WRAPPER TEST")
    print("="*70 + "\n")
    
    try:
        # Initialize wrapper
        llm = LLMWrapper(verbose=True)
        
        # Get provider info
        info = llm.get_provider_info()
        print(f"\nProvider: {info['provider']}")
        print(f"Model: {info['model']}\n")
        
        # Test with simple prompt
        test_prompt = "Explain what AWS S3 is in exactly one sentence."
        
        print(f"Test Prompt: {test_prompt}\n")
        print("Generating response...\n")
        
        response = llm.generate(test_prompt, max_tokens=100)
        
        print("="*70)
        print("RESPONSE:")
        print("="*70)
        print(response)
        print("="*70)
        
        print("\n✅ LLM Wrapper is working correctly!\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print("Please check:")
        print("  1. .env file exists with credentials")
        print("  2. AWS Bedrock access OR OpenAI API key configured")
        print("  3. Run: python tests/test_aws_bedrock.py\n")