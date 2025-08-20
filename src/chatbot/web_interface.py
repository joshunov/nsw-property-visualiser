#!/usr/bin/env python3
"""
Web Interface for Eastern Suburbs Property AI Chatbot
Flask-based web application for the AI-powered property chatbot
"""

from flask import Flask, render_template, request, jsonify
import logging
import os

# Configure logging
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler(os.path.join(logs_dir, "web_chatbot.log")), logging.StreamHandler()])

app = Flask(__name__)

# Try to initialize AI chatbot, fall back to basic if needed
try:
    from ai_chatbot import AIChatbot
    chatbot = AIChatbot(use_cache=True)
    print("🤖 AI chatbot initialized for web interface")
except Exception as e:
    print(f"⚠️  AI chatbot failed to initialize: {e}")
    try:
        from property_chatbot import PropertyChatbot
        chatbot = PropertyChatbot(use_cache=True)
        print("🔧 Basic chatbot initialized for web interface")
    except Exception as e2:
        print(f"❌ Failed to initialize any chatbot: {e2}")
        chatbot = None

@app.route('/')
def index():
    """Main page with chat interface"""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat queries"""
    try:
        if chatbot is None:
            return jsonify({'error': 'Chatbot not available'}), 500
            
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the query
        response = chatbot.process_query(user_message)
        
        return jsonify({
            'response': response,
            'suggestions': chatbot.get_suggestions()
        })
        
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/suggestions')
def get_suggestions():
    """Get suggested questions"""
    try:
        if chatbot is None:
            return jsonify({'error': 'Chatbot not available'}), 500
            
        return jsonify({
            'suggestions': chatbot.get_suggestions()
        })
    except Exception as e:
        logging.error(f"Error getting suggestions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🤖 Starting AI-Powered Eastern Suburbs Property Chatbot Web Interface")
    print("🌐 Open your browser and go to: http://localhost:5000")
    app.run(debug=False, host='0.0.0.0', port=5000)
