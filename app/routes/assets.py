from flask import request, jsonify
from app.routes import main_bp
from app import db
from app.models import Asset, Category, Entity, MovementLedger
from datetime import datetime

@main_bp.route('/api/categories/<int:category_id>/assets', methods=['POST'])
def create_asset(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    data = request.get_json()
    required_fields = ['name', 'purchase_date']
    if not data or not all(data.get(f) for f in required_fields):
        return jsonify({'error': f'Se requieren: {", ".join(required_fields)}'}), 400
    try:
        purchase_date = datetime.fromisoformat(data.get('purchase_date'))
    except:
        return jsonify({'error': 'purchase_date debe estar en formato ISO (YYYY-MM-DD)'}), 400
    asset = Asset(entity_id=category.entity_id, category_id=category_id, name=data.get('name'), description=data.get('description'), brand=data.get('brand'), model=data.get('model'), serial_number=data.get('serial_number'), purchase_date=purchase_date, purchase_price=data.get('purchase_price', 0), warranty_expiry=datetime.fromisoformat(data.get('warranty_expiry')) if data.get('warranty_expiry') else None, requires_maintenance=data.get('requires_maintenance', True), status=data.get('status', 'active'))
    db.session.add(asset)
    db.session.flush()
    if asset.purchase_price and asset.purchase_price > 0:
        movement = MovementLedger(entity_id=category.entity_id, asset_id=asset.id, movement_type='purchase', description=f'Compra: {asset.brand} {asset.model}', amount=asset.purchase_price, movement_date=purchase_date)
        db.session.add(movement)
    db.session.commit()
    return jsonify({'id': asset.id, 'name': asset.name, 'category_id': category_id, 'purchase_price': asset.purchase_price, 'created_at': asset.created_at.isoformat()}), 201

@main_bp.route('/api/categories/<int:category_id>/assets', methods=['GET'])
def list_assets(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    assets = Asset.query.filter_by(category_id=category_id).all()
    return jsonify([{'id': a.id, 'name': a.name, 'brand': a.brand, 'model': a.model, 'purchase_price': a.purchase_price, 'total_cost': a.get_total_cost(), 'requires_maintenance': a.requires_maintenance, 'status': a.status, 'warranty_status': a.get_warranty_status(), 'created_at': a.created_at.isoformat()} for a in assets]), 200

@main_bp.route('/api/assets/<int:asset_id>', methods=['GET'])
def get_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    return jsonify({'id': asset.id, 'name': asset.name, 'description': asset.description, 'brand': asset.brand, 'model': asset.model, 'serial_number': asset.serial_number, 'category_id': asset.category_id, 'purchase_date': asset.purchase_date.isoformat(), 'purchase_price': asset.purchase_price, 'total_cost': asset.get_total_cost(), 'warranty_expiry': asset.warranty_expiry.isoformat() if asset.warranty_expiry else None, 'warranty_status': asset.get_warranty_status(), 'requires_maintenance': asset.requires_maintenance, 'status': asset.status, 'movements_count': len(asset.movements), 'created_at': asset.created_at.isoformat(), 'updated_at': asset.updated_at.isoformat()}), 200

@main_bp.route('/api/assets/<int:asset_id>', methods=['PUT'])
def update_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    data = request.get_json()
    if 'name' in data:
        asset.name = data['name']
    if 'description' in data:
        asset.description = data['description']
    if 'brand' in data:
        asset.brand = data['brand']
    if 'model' in data:
        asset.model = data['model']
    if 'status' in data:
        asset.status = data['status']
    if 'requires_maintenance' in data:
        asset.requires_maintenance = data['requires_maintenance']
    asset.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'id': asset.id, 'name': asset.name, 'updated_at': asset.updated_at.isoformat()}), 200

@main_bp.route('/api/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    db.session.delete(asset)
    db.session.commit()
    return jsonify({'message': 'Activo eliminado'}), 200
