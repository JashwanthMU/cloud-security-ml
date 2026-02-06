"""
Production-ready Flask API
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from logger import logger
import os
import sys
sys.path.append('src')

from api.hybrid_analyzer import HybridAnalyzer
import logging
<<<<<<< HEAD

=======
>>>>>>> 0a16561e50242007f6cdd72c489ef569313b125c

app = Flask(__name__, 
            template_folder='../../frontend/templates',
            static_folder='../../frontend/static')
CORS(app)  # Allow requests from web browser
# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create hybrid analyzer instance
hybrid_analyzer = HybridAnalyzer()

# Route 1: Homepage
@app.route('/')
def home():
    """Serve the web UI"""
    return render_template('index.html')

# Route 2: Health check (for monitoring)
@app.route('/health')
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"})

# Route 3: Main analysis endpoint
@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze Terraform configuration using hybrid ML + LLM system"""

    logger.info("Received analysis request")

    try:
        data = request.json

        if not data or 'terraform_code' not in data:
            return jsonify({"error": "Missing terraform_code in request"}), 400

        terraform_code = data.get('terraform_code', '')

        logger.info(f"Code length: {len(terraform_code)} characters")

        # Use hybrid analyzer
        result = hybrid_analyzer.analyze_complete(terraform_code)

        logger.info(
            f"Analysis complete: {result.get('decision')} "
            f"(score: {result.get('risk_score')})"
        )

        return jsonify(result)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

<<<<<<< HEAD
=======

>>>>>>> 0a16561e50242007f6cdd72c489ef569313b125c

# Route 4: Upload file endpoint
@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """
    Analyze uploaded Terraform file
    """
    
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400
        
        if not file.filename.endswith('.tf'):
            return jsonify({"error": "File must be .tf (Terraform)"}), 400
        
        # Save temporarily
        temp_path = f'/tmp/{file.filename}'
        file.save(temp_path)
        
        # Analyze
        result = hybrid_analyzer.analyze_file(temp_path)
<<<<<<< HEAD

=======
>>>>>>> 0a16561e50242007f6cdd72c489ef569313b125c
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route 5: Batch analysis
@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple configurations at once
    """
    
    try:
        data = request.json
        
        if not data or 'configurations' not in data:
            return jsonify({"error": "Missing configurations array"}), 400
        
        configurations = data['configurations']
        
        results = []
        for i, config in enumerate(configurations):
            result = hybrid_analyzer.analyze_complete(config['code'])
            result['config_id'] = config.get('id', f'config_{i}')
            results.append(result)
        
        # Summary statistics
        summary = {
            'total': len(results),
            'blocked': len([r for r in results if r['overall_decision'] == 'BLOCK']),
            'warnings': len([r for r in results if r['overall_decision'] == 'WARN']),
            'allowed': len([r for r in results if r['overall_decision'] == 'ALLOW'])
        }
        
        return jsonify({
            'summary': summary,
            'results': results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Production settings
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=5000,
        debug=False,      # Turn off debug in production
        threaded=True     # Handle multiple requests
    )
