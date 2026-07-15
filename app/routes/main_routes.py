from flask import jsonify
from app.routes import main_bp

@main_bp.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Asset Management API',
        'version': '1.0.0',
        'status': 'running'
    })

@main_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200
