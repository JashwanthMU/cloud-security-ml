from flask import Flask, request, jsonify

# Create a Flask app
app = Flask(__name__)

# Route 1: Homepage
@app.route('/')
def home():
    return "Welcome to Cloud Security ML System!"

# Route 2: Analyze endpoint (this will be our main function)
@app.route('/analyze', methods=['POST'])
def analyze():
    # Get data sent by user
    data = request.json
    terraform_code = data.get('terraform_code', '')
    
    # Simple risk calculation (we'll make this smarter later)
    risk_score = 0.0
    problems = []
    
    # Check for risky patterns
    if 'public' in terraform_code.lower():
        risk_score += 0.4
        problems.append("Public access detected")
    
    if '0.0.0.0/0' in terraform_code:
        risk_score += 0.3
        problems.append("Open to entire internet")
    
    if 'password' in terraform_code.lower():
        risk_score += 0.2
        problems.append("Hardcoded password found")
    
    # Make decision
    if risk_score > 0.7:
        decision = "BLOCK"
    elif risk_score > 0.3:
        decision = "WARN"
    else:
        decision = "ALLOW"
    
    # Return result
    return jsonify({
        "decision": decision,
        "risk_score": risk_score,
        "problems": problems
    })

# Start the server
if __name__ == '__main__':
    app.run(debug=True, port=5000)