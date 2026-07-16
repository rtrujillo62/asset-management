from flask import jsonify
from app.routes import main_bp

@main_bp.route('/')
def home():
    return jsonify({'message': 'Asset Management API', 'status': 'running', 'version': '1.0.0'})

@main_bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})
