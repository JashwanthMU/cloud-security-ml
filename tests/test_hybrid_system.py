"""
Test suite for Hybrid ML+LLM System

"""

import pytest
import sys
sys.path.append('src')

from api.hybrid_analyzer import HybridAnalyzer

# Initialize analyzer once for all tests
analyzer = HybridAnalyzer()

class TestHybridAnalyzer:
    """Test hybrid ML+LLM system"""
    
    def test_high_risk_public_customer_data(self):
        """Should BLOCK public customer data"""
        
        code = '''
resource "aws_s3_bucket" "customer_db" {
  bucket = "prod-customer-database"
  acl    = "public-read"
}
'''
        
        result = analyzer.analyze(code)
        
        assert result['decision'] == 'BLOCK', "Should block public customer data"
        assert result['risk_score'] > 0.7, "Risk score should be high"
        assert result['intent'] in ['ACCIDENTAL', 'UNCERTAIN'], "Should detect as accidental"
    
    def test_safe_encrypted_bucket(self):
        """Should ALLOW secure configuration"""
        
        code = '''
resource "aws_s3_bucket" "secure_data" {
  bucket = "company-logs"
  acl    = "private"
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
'''
        
        result = analyzer.analyze(code)
        
        assert result['decision'] == 'ALLOW', "Should allow safe configuration"
        assert result['risk_score'] < 0.3, "Risk score should be low"
    
    def test_intentional_public_website(self):
        """Should WARN (not BLOCK) for intentional public website"""
        
        code = '''
resource "aws_s3_bucket" "marketing_site" {
  bucket = "company-public-website"
  acl    = "public-read"
  
  website {
    index_document = "index.html"
  }
  
  tags = {
    Purpose = "Marketing website"
  }
}
'''
        
        result = analyzer.analyze(code)
        
        # Should be WARN or ALLOW, NOT BLOCK
        assert result['decision'] != 'BLOCK', "Should not block intentional website"
        assert result['intent'] == 'INTENTIONAL', "Should detect as intentional"
    
    def test_ssh_open_to_world(self):
        """Should BLOCK SSH open to 0.0.0.0/0"""
        
        code = '''
resource "aws_security_group" "ssh" {
  name = "ssh_access"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
'''
        
        result = analyzer.analyze(code)
        
        assert result['decision'] == 'BLOCK', "Should block SSH open to world"
        assert result['risk_score'] > 0.6, "Risk should be high"
    
    def test_ml_llm_fusion(self):
        """Test that ML and LLM scores are being fused"""
        
        code = '''
resource "aws_s3_bucket" "test" {
  bucket = "test-bucket"
  acl    = "public-read"
}
'''
        
        result = analyzer.analyze(code)
        
        # Both scores should exist
        assert 'ml_score' in result, "ML score should be present"
        assert 'llm_score' in result, "LLM score should be present"
        
        # Final score should be between ML and LLM scores
        ml_score = result['ml_score']
        llm_score = result['llm_score']
        final_score = result['risk_score']
        
        min_score = min(ml_score, llm_score)
        max_score = max(ml_score, llm_score)
        
        assert min_score <= final_score <= max_score, "Final score should be fusion of ML and LLM"
    
    def test_recommendations_generated(self):
        """Test that recommendations are provided"""
        
        code = '''
resource "aws_s3_bucket" "data" {
  bucket = "unencrypted-bucket"
  acl    = "private"
}
'''
        
        result = analyzer.analyze(code)
        
        # Should have problems identified
        assert 'problems' in result, "Problems should be identified"
        assert len(result['problems']) > 0, "Should have at least one problem"

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_code(self):
        """Should handle empty code gracefully"""
        
        result = analyzer.analyze("")
        
        assert 'error' in result, "Should return error for empty code"
    
    def test_invalid_terraform(self):
        """Should handle invalid Terraform syntax"""
        
        code = "this is not terraform code"
        result = analyzer.analyze(code)
        
        assert 'error' in result, "Should return error for invalid code"
    
    def test_multiple_resources(self):
        """Should analyze first resource when multiple present"""
        
        code = '''
resource "aws_s3_bucket" "bucket1" {
  bucket = "bucket-one"
}

resource "aws_s3_bucket" "bucket2" {
  bucket = "bucket-two"
}
'''
        
        result = analyzer.analyze(code)
        
        assert 'decision' in result, "Should analyze successfully"
        assert result['resource']['name'] == 'bucket1', "Should analyze first resource"

# Performance tests
class TestPerformance:
    """Test system performance"""
    
    def test_analysis_speed(self):
        """Analysis should complete in reasonable time"""
        
        import time
        
        code = '''
resource "aws_s3_bucket" "test" {
  bucket = "test"
  acl    = "private"
}
'''
        
        start = time.time()
        result = analyzer.analyze(code)
        duration = time.time() - start
        
        assert duration < 10, f"Analysis took {duration}s, should be under 10s"
        print(f"✅ Analysis completed in {duration:.2f}s")

# Run tests
if __name__ == '__main__':
    print("=" * 60)
    print("Running Hybrid System Tests")
    print("=" * 60)
    
    # Run with verbose output
    pytest.main([__file__, '-v', '--tb=short'])