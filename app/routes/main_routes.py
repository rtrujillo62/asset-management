from flask import request, jsonify, redirect, url_for
from app.routes import main_bp
from app import db
from app.models import Entity
from datetime import datetime

@main_bp.route('/')
def home():
    return jsonify({'message': 'Asset Management API', 'status': 'running', 'version': '1.0.0'})

@main_bp.route('/form/entities', methods=['POST'])
def create_entity_form():
    """Procesa el formulario de creación de entidad"""
    name = request.form.get('name')
    entity_type = request.form.get('entity_type')
    location = request.form.get('location')
    
    if not name or not entity_type:
        return redirect(url_for('main.dashboard'))
    
    entity = Entity(
        name=name,
        entity_type=entity_type,
        location=location,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.session.add(entity)
    db.session.commit()
    
    return redirect(url_for('main.dashboard'))
