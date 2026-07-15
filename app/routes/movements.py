from flask import request, jsonify
from app.routes import main_bp
from app import db
from app.models import MovementLedger, Asset
from datetime import datetime

@main_bp.route('/api/assets/<int:asset_id>/movements', methods=['POST'])
def create_movement(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    data = request.get_json()
    required = ['movement_type', 'description', 'amount']
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': f'Se requieren: {", ".join(required)}'}), 400
    valid_types = ['purchase', 'maintenance', 'repair', 'replacement', 'depreciation', 'sale']
    if data.get('movement_type') not in valid_types:
        return jsonify({'error': f'movement_type debe ser uno de: {", ".join(valid_types)}'}), 400
    try:
        movement_date = datetime.fromisoformat(data.get('movement_date')) if data.get('movement_date') else datetime.utcnow()
    except:
        return jsonify({'error': 'movement_date debe estar en formato ISO'}), 400
    movement = MovementLedger(entity_id=asset.entity_id, asset_id=asset_id, movement_type=data.get('movement_type'), description=data.get('description'), amount=float(data.get('amount')), maintenance_plan_id=data.get('maintenance_plan_id'), movement_date=movement_date, notes=data.get('notes'))
    db.session.add(movement)
    db.session.commit()
    return jsonify({'id': movement.id, 'movement_type': movement.movement_type, 'amount': movement.amount, 'movement_date': movement.movement_date.isoformat(), 'created_at': movement.created_at.isoformat()}), 201

@main_bp.route('/api/assets/<int:asset_id>/movements', methods=['GET'])
def list_movements(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    movements = MovementLedger.query.filter_by(asset_id=asset_id).order_by(MovementLedger.movement_date.desc()).all()
    return jsonify([{'id': m.id, 'movement_type': m.movement_type, 'description': m.description, 'amount': m.amount, 'movement_date': m.movement_date.isoformat(), 'notes': m.notes, 'created_at': m.created_at.isoformat()} for m in movements]), 200

@main_bp.route('/api/movements/<int:movement_id>', methods=['GET'])
def get_movement(movement_id):
    movement = MovementLedger.query.get(movement_id)
    if not movement:
        return jsonify({'error': 'Movimiento no encontrado'}), 404
    return jsonify({'id': movement.id, 'asset_id': movement.asset_id, 'entity_id': movement.entity_id, 'movement_type': movement.movement_type, 'description': movement.description, 'amount': movement.amount, 'maintenance_plan_id': movement.maintenance_plan_id, 'movement_date': movement.movement_date.isoformat(), 'notes': movement.notes, 'created_at': movement.created_at.isoformat()}), 200

@main_bp.route('/api/assets/<int:asset_id>/movements/summary', methods=['GET'])
def get_movements_summary(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    summary = {}
    total = 0
    for movement_type in ['purchase', 'maintenance', 'repair', 'replacement', 'depreciation', 'sale']:
        amount = MovementLedger.get_asset_by_type(asset_id, movement_type)
        summary[movement_type] = amount
        total += amount
    return jsonify({'asset_id': asset_id, 'total_cost': total, 'by_type': summary, 'movements_count': len(asset.movements)}), 200

@main_bp.route('/api/movements/<int:movement_id>', methods=['PUT'])
def update_movement(movement_id):
    movement = MovementLedger.query.get(movement_id)
    if not movement:
        return jsonify({'error': 'Movimiento no encontrado'}), 404
    data = request.get_json()
    if 'description' in data:
        movement.description = data['description']
    if 'amount' in data:
        movement.amount = float(data['amount'])
    if 'notes' in data:
        movement.notes = data['notes']
    db.session.commit()
    return jsonify({'id': movement.id, 'amount': movement.amount, 'description': movement.description}), 200

@main_bp.route('/api/movements/<int:movement_id>', methods=['DELETE'])
def delete_movement(movement_id):
    movement = MovementLedger.query.get(movement_id)
    if not movement:
        return jsonify({'error': 'Movimiento no encontrado'}), 404
    db.session.delete(movement)
    db.session.commit()
    return jsonify({'message': 'Movimiento eliminado'}), 200
