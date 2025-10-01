
"""
Personal cabinet (Личный кабинет) router for UPAK
Handles user dashboard, cards list, payments list, and payment creation
"""

from flask import Blueprint, request, jsonify
import sqlite3
import os
from datetime import datetime, timedelta
from routers.auth_router import get_current_user

lk_bp = Blueprint('lk', __name__)

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////tmp/upak_test/upak_test.db')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', 'test_shop_id')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_secret_key')

def get_db_connection():
    """Get database connection"""
    db_path = DATABASE_URL.replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@lk_bp.route('/me', methods=['GET'])
@get_current_user
def get_user_info(user):
    """
    GET /me - Get current user information and subscription details
    Returns: { email, subscription_type, subscription_expires, cards_limit, cards_used }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's active Pro subscription if exists
        cursor.execute('''
            SELECT remaining_cards, expires_at 
            FROM pro_subscriptions 
            WHERE user_id = ? AND is_active = 1 AND expires_at > ?
            ORDER BY expires_at DESC LIMIT 1
        ''', (user['id'], datetime.utcnow().isoformat()))
        
        pro_sub = cursor.fetchone()
        conn.close()
        
        # Determine subscription type and limits
        if pro_sub:
            subscription_type = 'pro'
            subscription_expires = pro_sub['expires_at']
            cards_limit = 10  # Pro package has 10 cards
            cards_used = 10 - pro_sub['remaining_cards']
        else:
            subscription_type = user.get('subscription_type', 'free')
            subscription_expires = user.get('subscription_expires')
            cards_limit = user.get('cards_limit', 0)
            cards_used = user.get('cards_used', 0)
        
        return jsonify({
            'email': user['email'],
            'subscription_type': subscription_type,
            'subscription_expires': subscription_expires,
            'cards_limit': cards_limit,
            'cards_used': cards_used
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user info: {str(e)}'}), 500

@lk_bp.route('/cards', methods=['GET'])
@get_current_user
def get_user_cards(user):
    """
    GET /cards?limit=&offset= - Get user's cards list
    Returns: [{ id, title, created_at, pdf_url }]
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Limit maximum to prevent abuse
        limit = min(limit, 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, created_at, pdf_url
            FROM cards
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (user['id'], limit, offset))
        
        cards = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': card['id'],
            'title': card['title'],
            'created_at': card['created_at'],
            'pdf_url': card['pdf_url']
        } for card in cards])
        
    except Exception as e:
        return jsonify({'error': f'Failed to get cards: {str(e)}'}), 500

@lk_bp.route('/payments', methods=['GET'])
@get_current_user
def get_user_payments(user):
    """
    GET /payments?limit= - Get user's payments list
    Returns: [{ id, amount, status, subscription_type, created_at }]
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        
        # Limit maximum to prevent abuse
        limit = min(limit, 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, amount, status, package as subscription_type, created_at
            FROM payments
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user['id'], limit))
        
        payments = cursor.fetchall()
        conn.close()
        
        return jsonify([{
            'id': payment['id'],
            'amount': payment['amount'],
            'status': payment['status'],
            'subscription_type': payment['subscription_type'],
            'created_at': payment['created_at']
        } for payment in payments])
        
    except Exception as e:
        return jsonify({'error': f'Failed to get payments: {str(e)}'}), 500

@lk_bp.route('/payments/create', methods=['POST'])
@get_current_user
def create_payment(user):
    """
    POST /payments/create { package: 'start'|'pro' } - Create payment
    Returns: { confirmation_url } (redirect to YooKassa)
    """
    try:
        data = request.get_json()
        package = data.get('package', 'start').lower()
        
        if package not in ['start', 'pro']:
            return jsonify({'error': 'Invalid package. Use "start" or "pro"'}), 400
        
        # Determine package parameters
        if package == 'start':
            amount = 349.0
            description = "UPAK Start - Одна карточка товара"
        else:  # pro
            amount = 2490.0
            description = "UPAK Pro - 10 карточек на месяц"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create payment record
        cursor.execute('''
            INSERT INTO payments (user_id, amount, status, package, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user['id'], amount, 'pending', package, datetime.utcnow().isoformat()))
        
        payment_id = cursor.lastrowid
        conn.commit()
        
        # In production, integrate with YooKassa API
        # For now, return a test confirmation URL
        confirmation_url = f"https://yoomoney.ru/checkout/payments/v2/contract?orderId=test_{payment_id}"
        
        # Update payment with confirmation URL
        cursor.execute('''
            UPDATE payments SET confirmation_url = ? WHERE id = ?
        ''', (confirmation_url, payment_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'payment_id': payment_id,
            'confirmation_url': confirmation_url,
            'amount': amount,
            'package': package
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to create payment: {str(e)}'}), 500
