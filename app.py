#!/usr/bin/env python3
"""
UPAK Ecosystem - Main API Application
Features: REST API, Webhooks, Telegram Bot Integration
"""

import os
import time
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
from datetime import datetime

app = Flask(__name__)

# Rate limiting setup
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

# Configuration
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'default-secret-key')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.1.0'
    })

@app.route('/api/v1/status', methods=['GET'])
@limiter.limit("50 per minute")
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_version': '1.1.0',
        'status': 'operational',
        'features': ['webhooks', 'telegram_bot', 'rate_limiting'],
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/v1/data', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def handle_data():
    """Main data handling endpoint"""
    if request.method == 'GET':
        return jsonify({
            'message': 'UPAK Data Endpoint',
            'method': 'GET',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        logger.info(f"Received POST data: {data}")
        
        # Process data here
        response = {
            'message': 'Data processed successfully',
            'received_data': data,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 201

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Secure webhook endpoint"""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        logger.warning("Webhook received without signature")
        return jsonify({'error': 'Missing signature'}), 401
    
    # Validate signature
    payload = request.get_data()
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning("Invalid webhook signature")
        return jsonify({'error': 'Invalid signature'}), 401
    
    # Process webhook
    webhook_data = request.get_json()
    logger.info(f"Valid webhook received: {webhook_data}")
    
    # Send notification to Telegram if configured
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        send_telegram_notification(f"Webhook received: {webhook_data.get('event', 'unknown')}")
    
    return jsonify({'status': 'webhook processed'}), 200

@app.route('/telegram/send', methods=['POST'])
@limiter.limit("10 per minute")
def send_telegram_message():
    """Send message via Telegram bot"""
    if not TELEGRAM_BOT_TOKEN:
        return jsonify({'error': 'Telegram bot not configured'}), 400
    
    data = request.get_json()
    message = data.get('message', '')
    chat_id = data.get('chat_id', TELEGRAM_CHAT_ID)
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    success = send_telegram_notification(message, chat_id)
    
    if success:
        return jsonify({'status': 'message sent'}), 200
    else:
        return jsonify({'error': 'Failed to send message'}), 500

def send_telegram_notification(message, chat_id=None):
    """Send notification to Telegram"""
    if not TELEGRAM_BOT_TOKEN:
        return False
    
    chat_id = chat_id or TELEGRAM_CHAT_ID
    if not chat_id:
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': str(e.description)
    }), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
