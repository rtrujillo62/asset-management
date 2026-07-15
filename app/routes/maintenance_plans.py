from flask import request, jsonify
from app.routes import main_bp
from app import db
from app.models import MaintenancePlan, Asset, Category, Entity, MovementLedger
from datetime import datetime, timedelta

@main_bp.route('/api/assets/<int:asset_id>/maintenance-plans', methods=['POST'])
def create_maintenance_plan_for_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        return jsonify({'error': 'Activo no encontrado'}), 404
    data = request.get_json()
    required = ['name', 'interval_value']
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': f'Se requieren: {", ".join(required)}'}), 400
    
    interval_type = data.get('interval_type', 'days')
    valid_types = ['days', 'kilometers', 'hours', 'combined']
    if interval_type not in valid_types:
        return jsonify({'error': f'interval_type debe ser uno de: {", ".join(valid_types)}'}), 400
    
    plan = MaintenancePlan(
        entity_id=asset.entity_id,
        asset_id=asset_id,
        category_id=None,
        name=data.get('name'),
        description=data.get('description'),
        interval_type=interval_type,
        interval_value=float(data.get('interval_value')),
        secondary_type=data.get('secondary_type'),
        secondary_value=float(data.get('secondary_value')) if data.get('secondary_value') else None,
        estimated_cost=data.get('estimated_cost', 0),
        is_active=True
    )
    
    plan.calculate_next_due()
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'interval_type': plan.interval_type,
        'interval_value': plan.interval_value,
        'secondary_type': plan.secondary_type,
        'secondary_value': plan.secondary_value,
        'next_due': plan.next_due.isoformat() if plan.next_due else None,
        'created_at': plan.created_at.isoformat()
    }), 201

@main_bp.route('/api/categories/<int:category_id>/maintenance-plans', methods=['POST'])
def create_maintenance_plan_for_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Categoría no encontrada'}), 404
    data = request.get_json()
    required = ['name', 'interval_value']
    if not data or not all(data.get(f) for f in required):
        return jsonify({'error': f'Se requieren: {", ".join(required)}'}), 400
    
    interval_type = data.get('interval_type', 'days')
    valid_types = ['days', 'kilometers', 'hours', 'combined']
    if interval_type not in valid_types:
        return jsonify({'error': f'interval_type debe ser uno de: {", ".join(valid_types)}'}), 400
    
    plan = MaintenancePlan(
        entity_id=category.entity_id,
        asset_id=None,
        category_id=category_id,
        name=data.get('name'),
        description=data.get('description'),
        interval_type=interval_type,
        interval_value=float(data.get('interval_value')),
        secondary_type=data.get('secondary_type'),
        secondary_value=float(data.get('secondary_value')) if data.get('secondary_value') else None,
        estimated_cost=data.get('estimated_cost', 0),
        is_active=True
    )
    
    plan.calculate_next_due()
    db.session.add(plan)
    db.session.commit()
    
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'interval_type': plan.interval_type,
        'interval_value': plan.interval_value,
        'secondary_type': plan.secondary_type,
        'secondary_value': plan.secondary_value,
        'next_due': plan.next_due.isoformat() if plan.next_due else None,
        'created_at': plan.created_at.isoformat()
    }), 201

@main_bp.route('/api/maintenance-plans', methods=['GET'])
def list_all_maintenance_plans():
    plans = MaintenancePlan.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'interval_type': p.interval_type,
        'interval_value': p.interval_value,
        'secondary_type': p.secondary_type,
        'secondary_value': p.secondary_value,
        'estimated_cost': p.estimated_cost,
        'asset_id': p.asset_id,
        'category_id': p.category_id,
        'next_due': p.next_due.isoformat() if p.next_due else None,
        'is_overdue': p.is_overdue(),
        'days_until_due': p.days_until_due(),
        'status': p.get_status(),
        'created_at': p.created_at.isoformat()
    } for p in plans]), 200

@main_bp.route('/api/maintenance-plans/<int:plan_id>', methods=['GET'])
def get_maintenance_plan(plan_id):
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'description': plan.description,
        'interval_type': plan.interval_type,
        'interval_value': plan.interval_value,
        'secondary_type': plan.secondary_type,
        'secondary_value': plan.secondary_value,
        'estimated_cost': plan.estimated_cost,
        'asset_id': plan.asset_id,
        'category_id': plan.category_id,
        'last_execution': plan.last_execution.isoformat() if plan.last_execution else None,
        'last_kilometers': plan.last_kilometers,
        'last_hours': plan.last_hours,
        'next_due': plan.next_due.isoformat() if plan.next_due else None,
        'is_overdue': plan.is_overdue(),
        'days_until_due': plan.days_until_due(),
        'status': plan.get_status(),
        'is_active': plan.is_active,
        'movements_count': len(plan.movements),
        'created_at': plan.created_at.isoformat(),
        'updated_at': plan.updated_at.isoformat()
    }), 200

@main_bp.route('/api/maintenance-plans/<int:plan_id>', methods=['PUT'])
def update_maintenance_plan(plan_id):
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    data = request.get_json()
    if 'name' in data:
        plan.name = data['name']
    if 'description' in data:
        plan.description = data['description']
    if 'interval_value' in data:
        plan.interval_value = float(data['interval_value'])
    if 'interval_type' in data:
        plan.interval_type = data['interval_type']
    if 'secondary_type' in data:
        plan.secondary_type = data['secondary_type']
    if 'secondary_value' in data:
        plan.secondary_value = float(data['secondary_value']) if data['secondary_value'] else None
    if 'estimated_cost' in data:
        plan.estimated_cost = data['estimated_cost']
    if 'is_active' in data:
        plan.is_active = data['is_active']
    plan.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({
        'id': plan.id,
        'name': plan.name,
        'updated_at': plan.updated_at.isoformat()
    }), 200

@main_bp.route('/api/maintenance-plans/<int:plan_id>/execute', methods=['POST'])
def execute_maintenance_plan(plan_id):
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    data = request.get_json()
    plan.last_execution = datetime.utcnow()
    if data.get('last_kilometers'):
        plan.last_kilometers = float(data.get('last_kilometers'))
    if data.get('last_hours'):
        plan.last_hours = float(data.get('last_hours'))
    plan.calculate_next_due()
    if data.get('actual_cost'):
        movement = MovementLedger(entity_id=plan.entity_id, asset_id=plan.asset_id, movement_type='maintenance', description=f'Mantenimiento: {plan.name}', amount=float(data.get('actual_cost')), maintenance_plan_id=plan_id, movement_date=datetime.utcnow(), notes=data.get('notes'))
        db.session.add(movement)
    db.session.commit()
    return jsonify({
        'id': plan.id,
        'last_execution': plan.last_execution.isoformat(),
        'last_kilometers': plan.last_kilometers,
        'last_hours': plan.last_hours,
        'next_due': plan.next_due.isoformat() if plan.next_due else None
    }), 200

@main_bp.route('/api/maintenance-plans/<int:plan_id>', methods=['DELETE'])
def delete_maintenance_plan(plan_id):
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan no encontrado'}), 404
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Plan eliminado'}), 200
