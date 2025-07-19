from flask import Flask, request, jsonify, render_template
from scraper import GSTScraper
import json
import os
app = Flask(__name__)

# Initialize scraper instance
scraper = None

def get_scraper():
    """Get or create scraper instance"""
    global scraper
    if scraper is None:
        scraper = GSTScraper(headless=True)
    return scraper

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/verify-gst', methods=['POST'])
def verify_gst():
    """API endpoint to verify GST number"""
    try:
        data = request.get_json()
        gst_number = data.get('gst_number', '').strip()
        
        if not gst_number:
            return jsonify({
                'success': False,
                'error': 'GST number is required'
            }), 400
        
        # Get scraper instance and scrape data
        scraper_instance = get_scraper()
        result = scraper_instance.scrape_gst_data(gst_number)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/verify-gst-console', methods=['POST'])
def verify_gst_console():
    """Console-friendly API endpoint"""
    try:
        data = request.get_json()
        gst_number = data.get('gst_number', '').strip()
        
        if not gst_number:
            return jsonify({
                'success': False,
                'error': 'GST number is required'
            }), 400
        
        # Get scraper instance and scrape data
        scraper_instance = get_scraper()
        result = scraper_instance.scrape_gst_data(gst_number)
        
        # Format for console output
        if result['success']:
            console_output = format_console_output(result)
            return jsonify({
                'success': True,
                'console_output': console_output,
                'raw_data': result['data']
            }), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

def format_console_output(result):
    """Format the result for console display"""
    output = []
    output.append("="*60)
    output.append("GST NUMBER VERIFICATION RESULT")
    output.append("="*60)
    output.append(f"GST Number: {result['gst_number']}")
    output.append("-"*60)
    
    data = result['data']
    if data:
        for key, value in data.items():
            formatted_key = key.replace('_', ' ').title()
            output.append(f"{formatted_key:<20}: {value}")
    else:
        output.append("No additional data found")
    
    output.append("="*60)
    return "\n".join(output)

@app.route('/console-test')
def console_test():
    """Test endpoint for console usage"""
    return """
    <h2>Console Test</h2>
    <p>Use this endpoint to test GST verification:</p>
    <pre>
curl -X POST http://localhost:5000/api/verify-gst-console \
  -H "Content-Type: application/json" \
  -d '{"gst_number": "37AAACP2678Q1ZP"}'
    </pre>
    """

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        print("Starting GST Scraper Flask App...")
        print("Available endpoints:")
        print("- GET  /                          - Web interface")
        print("- POST /api/verify-gst            - JSON API")
        print("- POST /api/verify-gst-console    - Console-friendly API")
        print("- GET  /console-test              - Console test instructions")
        print("\nStarting server on http://localhost:5000")
        
        
        port = int(os.environ.get('PORT', 5000))
        app.run(debug= False,host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up scraper instance
        if scraper:
            scraper.close()