from flask import jsonify, redirect, url_for
from app.routes import main_bp

@main_bp.route('/')
def home():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/api')
def api_info():
    return jsonify({'message': 'Asset Management API', 'status': 'running', 'version': '1.0.0'})

@main_bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})
