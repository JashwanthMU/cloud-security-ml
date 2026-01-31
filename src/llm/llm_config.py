"""
LLM Configuration - supports both AWS Bedrock and OpenAI
"""

import os
from dotenv import load_dotenv

load_dotenv()

class LLMConfig:
    """Manages LLM provider configuration"""
    
    def __init__(self):
        self.provider = os.getenv('LLM_PROVIDER', 'openai')  # 'openai' or 'bedrock'
        
        if self.provider == 'openai':
            self.api_key = os.getenv('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in .env file")
        
        elif self.provider == 'bedrock':
            self.region = os.getenv('AWS_REGION', 'us-east-1')
            self.model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
    
    def get_config(self):
        """Returns configuration dictionary"""
        if self.provider == 'openai':
            return {
                'provider': 'openai',
                'model': 'gpt-3.5-turbo',
                'api_key': self.api_key
            }
        else:
            return {
                'provider': 'bedrock',
                'model_id': self.model_id,
                'region': self.region
            }

# Test
if __name__ == '__main__':
    config = LLMConfig()
    print("LLM Configuration:")
    print(config.get_config())