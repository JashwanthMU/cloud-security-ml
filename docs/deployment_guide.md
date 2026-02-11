# Deployment Guide

## Prerequisites

- Python 3.9+
- Git
- AWS Account (optional for Bedrock)
- OpenAI API Key

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/JashwanthMU/cloud-security-ml.git
cd cloud-security-ml
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your keys
notepad .env
```

Required variables:
```
OPENAI_API_KEY=sk-your-key-here
```

### 4. Generate Example Data
```bash
python scripts/generate_examples.py
```

### 5. Start Server
```bash
python src/api/app.py
```

Server runs at: http://localhost:5000

## Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Test specific module
python -m pytest tests/test_hybrid_system.py -v
```

## Production Deployment (Week 4)

Coming soon: Docker, AWS Lambda, CI/CD