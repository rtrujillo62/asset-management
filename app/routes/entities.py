from flask import request, jsonify
from app.routes import main_bp
from app import db
from app.models import Entity
from datetime import datetime

@main_bp.route('/api/entities', methods=['POST'])
def create_entity():
    data = request.get_json()
    if not data or not data.get('name') or not data.get('entity_type'):
        return jsonify({'error': 'name y entity_type son requeridos'}), 400
    if data.get('entity_type') not in ['casa', 'empresa']:
        return jsonify({'error': 'entity_type debe ser "casa" o "empresa"'}), 400
    if Entity.query.filter_by(name=data.get('name')).first():
        return jsonify({'error': 'Esta entidad ya existe'}), 409
    entity = Entity(name=data.get('name'), entity_type=data.get('entity_type'), description=data.get('description'), location=data.get('location'))
    db.session.add(entity)
    db.session.commit()
    return jsonify({'id': entity.id, 'name': entity.name, 'entity_type': entity.entity_type, 'created_at': entity.created_at.isoformat()}), 201

@main_bp.route('/api/entities', methods=['GET'])
def list_entities():
    entities = Entity.query.all()
    return jsonify([{'id': e.id, 'name': e.name, 'entity_type': e.entity_type, 'description': e.description, 'location': e.location, 'created_at': e.created_at.isoformat(), 'assets_count': len(e.assets), 'categories_count': len(e.categories)} for e in entities]), 200

@main_bp.route('/api/entities/<int:entity_id>', methods=['GET'])
def get_entity(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entidad no encontrada'}), 404
    return jsonify({'id': entity.id, 'name': entity.name, 'entity_type': entity.entity_type, 'description': entity.description, 'location': entity.location, 'created_at': entity.created_at.isoformat(), 'updated_at': entity.updated_at.isoformat(), 'assets_count': len(entity.assets), 'categories': [{'id': c.id, 'name': c.name} for c in entity.categories], 'maintenance_plans_count': len(entity.maintenance_plans)}), 200

@main_bp.route('/api/entities/<int:entity_id>', methods=['PUT'])
def update_entity(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entidad no encontrada'}), 404
    data = request.get_json()
    if 'name' in data:
        entity.name = data['name']
    if 'description' in data:
        entity.description = data['description']
    if 'location' in data:
        entity.location = data['location']
    entity.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'id': entity.id, 'name': entity.name, 'updated_at': entity.updated_at.isoformat()}), 200

@main_bp.route('/api/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entidad no encontrada'}), 404
    db.session.delete(entity)
    db.session.commit()
    return jsonify({'message': 'Entidad eliminada'}), 200
