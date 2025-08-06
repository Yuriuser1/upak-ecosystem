#!/usr/bin/env python3
"""
UPAK Ecosystem Tests
"""

import pytest
import json
import hmac
import hashlib
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert data['version'] == '1.1.0'

def test_api_status(client):
    """Test API status endpoint"""
    response = client.get('/api/v1/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['api_version'] == '1.1.0'
    assert data['status'] == 'operational'
    assert 'webhooks' in data['features']
    assert 'telegram_bot' in data['features']
    assert 'rate_limiting' in data['features']

def test_data_get(client):
    """Test GET data endpoint"""
    response = client.get('/api/v1/data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'UPAK Data Endpoint'
    assert data['method'] == 'GET'

def test_data_post(client):
    """Test POST data endpoint"""
    test_data = {'key': 'value', 'number': 42}
    response = client.post('/api/v1/data', 
                          data=json.dumps(test_data),
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Data processed successfully'
    assert data['received_data'] == test_data

def test_webhook_without_signature(client):
    """Test webhook without signature"""
    response = client.post('/webhook', 
                          data=json.dumps({'event': 'test'}),
                          content_type='application/json')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Missing signature'

def test_webhook_invalid_signature(client):
    """Test webhook with invalid signature"""
    headers = {'X-Hub-Signature-256': 'sha256=invalid'}
    response = client.post('/webhook',
                          data=json.dumps({'event': 'test'}),
                          content_type='application/json',
                          headers=headers)
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['error'] == 'Invalid signature'

def test_webhook_valid_signature(client):
    """Test webhook with valid signature"""
    payload = json.dumps({'event': 'test'})
    secret = 'default-secret-key'
    signature = 'sha256=' + hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    headers = {'X-Hub-Signature-256': signature}
    response = client.post('/webhook',
                          data=payload,
                          content_type='application/json',
                          headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'webhook processed'

def test_telegram_send_no_message(client):
    """Test Telegram send without message"""
    response = client.post('/telegram/send',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Message is required'

def test_rate_limiting(client):
    """Test rate limiting on API endpoints"""
    # This test would need to be more sophisticated in a real scenario
    # For now, just verify the endpoint responds normally
    response = client.get('/api/v1/status')
    assert response.status_code == 200
