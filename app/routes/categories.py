from flask import request, jsonify
from app.routes import main_bp
from app import db
from app.models import Category, Entity
from datetime import datetime

@main_bp.route('/api/entities/<int:entity_id>/categories', methods=['POST'])
def create_category(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entidad no encontrada'}), 404
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'error': 'name es requerido'}), 400
    existing = Category.query.filter_by(entity_id=entity_id, name=data.get('name')).first()
    if existing:
        return jsonify({'error': 'Esta categoría ya existe en esta entidad'}), 409
    category = Category(entity_id=entity_id, name=data.get('name'), description=data.get('description'))
    db.session.add(category)
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name, 'entity_id': entity_id, 'created_at': category.created_at.isoformat()}), 201

@main_bp.route('/api/entities/<int:entity_id>/categories', methods=['GET'])
def list_categories(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        return jsonify({'error': 'Entidad no encontrada'}), 404
    categories = Category.query.filter_by(entity_id=entity_id).all()
    return jsonify([{'id': c.id, 'name': c.name, 'description': c.description, 'assets_count': len(c.assets), 'created_at': c.created_at.isoformat()} for c in categories]), 200

@main_bp.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    return jsonify({'id': category.id, 'name': category.name, 'description': category.description, 'entity_id': category.entity_id, 'assets': [{'id': a.id, 'name': a.name} for a in category.assets], 'created_at': category.created_at.isoformat(), 'updated_at': category.updated_at.isoformat()}), 200

@main_bp.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    data = request.get_json()
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    category.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'id': category.id, 'name': category.name, 'updated_at': category.updated_at.isoformat()}), 200

@main_bp.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Categoría eliminada'}), 200
