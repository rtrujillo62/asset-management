from flask import request, redirect, url_for, abort
from app.routes import main_bp
from app import db
from app.models import Entity, Category, Asset, MaintenancePlan, MovementLedger
from datetime import datetime

@main_bp.route('/form/entities', methods=['POST'])
def create_entity_form():
    name = request.form.get('name')
    entity_type = request.form.get('entity_type')
    if not name or not entity_type:
        return redirect(url_for('main.dashboard'))
    entity = Entity(name=name, entity_type=entity_type,
                    location=request.form.get('location') or None)
    db.session.add(entity)
    db.session.commit()
    return redirect(url_for('main.ver_entidad', entity_id=entity.id))

@main_bp.route('/form/entidad/<int:entity_id>/categories', methods=['POST'])
def create_category_form(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        abort(404)
    name = request.form.get('name')
    if not name:
        return redirect(url_for('main.ver_entidad', entity_id=entity_id))
    category = Category(entity_id=entity.id, name=name,
                        description=request.form.get('description') or None)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('main.ver_categoria', category_id=category.id))

@main_bp.route('/form/categoria/<int:category_id>/assets', methods=['POST'])
def create_asset_form(category_id):
    category = Category.query.get(category_id)
    if not category:
        abort(404)
    name = request.form.get('name')
    purchase_date = request.form.get('purchase_date')
    if not name or not purchase_date:
        return redirect(url_for('main.ver_categoria', category_id=category_id))

    price = float(request.form.get('purchase_price') or 0)
    fecha = datetime.fromisoformat(purchase_date)
    km = request.form.get('current_kilometers')
    hrs = request.form.get('current_hours')

    asset = Asset(
        entity_id=category.entity_id,
        category_id=category.id,
        name=name,
        brand=request.form.get('brand') or None,
        model=request.form.get('model') or None,
        year=int(request.form.get('year')) if request.form.get('year') else None,
        serial_number=request.form.get('serial_number') or None,
        purchase_date=fecha,
        purchase_price=price,
        current_kilometers=float(km) if km else None,
        current_hours=float(hrs) if hrs else None,
        last_reading_date=datetime.utcnow() if (km or hrs) else None,
        requires_maintenance=bool(request.form.get('requires_maintenance')),
        status='active'
    )
    db.session.add(asset)
    db.session.flush()

    if price > 0:
        db.session.add(MovementLedger(
            entity_id=asset.entity_id, asset_id=asset.id,
            movement_type='purchase', description=f'Compra: {asset.name}',
            amount=price, movement_date=fecha
        ))

    db.session.commit()
    return redirect(url_for('main.ver_activo', asset_id=asset.id))

@main_bp.route('/form/activo/<int:asset_id>/lectura', methods=['POST'])
def reportar_lectura(asset_id):
    """Actualiza el odómetro / horómetro del activo"""
    asset = Asset.query.get(asset_id)
    if not asset:
        abort(404)
    km = request.form.get('current_kilometers')
    hrs = request.form.get('current_hours')
    if km:
        asset.current_kilometers = float(km)
    if hrs:
        asset.current_hours = float(hrs)
    if km or hrs:
        asset.last_reading_date = datetime.utcnow()
        db.session.commit()
    return redirect(url_for('main.ver_activo', asset_id=asset.id))

@main_bp.route('/form/activo/<int:asset_id>/maintenance-plans', methods=['POST'])
def create_plan_form(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        abort(404)
    name = request.form.get('name')
    interval_value = request.form.get('interval_value')
    if not name or not interval_value:
        return redirect(url_for('main.ver_activo', asset_id=asset_id))

    secondary_value = request.form.get('secondary_value')
    secondary_type = request.form.get('secondary_type') or None
    if not secondary_value:
        secondary_type = None

    plan = MaintenancePlan(
        entity_id=asset.entity_id,
        asset_id=asset.id,
        name=name,
        description=request.form.get('description') or None,
        interval_type=request.form.get('interval_type', 'days'),
        interval_value=float(interval_value),
        secondary_type=secondary_type,
        secondary_value=float(secondary_value) if secondary_value else None,
        estimated_cost=float(request.form.get('estimated_cost') or 0),
        is_active=True
    )

    # Punto de partida: cuándo/dónde se hizo el último mantenimiento.
    # Si no lo indican, se asume que se hace hoy con la lectura actual.
    ultima_fecha = request.form.get('last_execution')
    ultimo_km = request.form.get('last_kilometers')
    ultimas_hrs = request.form.get('last_hours')

    plan.last_execution = datetime.fromisoformat(ultima_fecha) if ultima_fecha else datetime.utcnow()

    if plan.usa_tipo('kilometers'):
        plan.last_kilometers = float(ultimo_km) if ultimo_km else (asset.current_kilometers or 0)
    if plan.usa_tipo('hours'):
        plan.last_hours = float(ultimas_hrs) if ultimas_hrs else (asset.current_hours or 0)

    plan.calculate_next_due()

    db.session.add(plan)
    db.session.commit()
    return redirect(url_for('main.ver_activo', asset_id=asset.id))

@main_bp.route('/form/plan/<int:plan_id>/ejecutar', methods=['POST'])
def ejecutar_plan(plan_id):
    """Marca el mantenimiento como realizado y registra el costo real"""
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        abort(404)
    asset = plan.asset

    # Si reportan lectura al momento de ejecutar, se actualiza primero
    km = request.form.get('current_kilometers')
    hrs = request.form.get('current_hours')
    if asset and km:
        asset.current_kilometers = float(km)
        asset.last_reading_date = datetime.utcnow()
    if asset and hrs:
        asset.current_hours = float(hrs)
        asset.last_reading_date = datetime.utcnow()

    plan.registrar_ejecucion()

    costo = request.form.get('actual_cost')
    if costo and float(costo) > 0:
        db.session.add(MovementLedger(
            entity_id=plan.entity_id,
            asset_id=plan.asset_id,
            movement_type='maintenance',
            description=f'Mantenimiento: {plan.name}',
            amount=float(costo),
            maintenance_plan_id=plan.id,
            movement_date=datetime.utcnow(),
            notes=request.form.get('notes') or None
        ))

    db.session.commit()
    return redirect(url_for('main.ver_activo', asset_id=plan.asset_id))
