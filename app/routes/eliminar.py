from flask import redirect, url_for, abort
from app.routes import main_bp
from app import db
from app.models import Entity, Category, Asset, MaintenancePlan

@main_bp.route('/eliminar/entidad/<int:entity_id>', methods=['POST'])
def eliminar_entidad(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        abort(404)
    db.session.delete(entity)   # cascade borra categorías, activos, planes y movimientos
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main_bp.route('/eliminar/categoria/<int:category_id>', methods=['POST'])
def eliminar_categoria(category_id):
    category = Category.query.get(category_id)
    if not category:
        abort(404)
    entity_id = category.entity_id
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('main.ver_entidad', entity_id=entity_id))

@main_bp.route('/eliminar/activo/<int:asset_id>', methods=['POST'])
def eliminar_activo(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        abort(404)
    category_id = asset.category_id
    db.session.delete(asset)
    db.session.commit()
    return redirect(url_for('main.ver_categoria', category_id=category_id))

@main_bp.route('/eliminar/plan/<int:plan_id>', methods=['POST'])
def eliminar_plan(plan_id):
    plan = MaintenancePlan.query.get(plan_id)
    if not plan:
        abort(404)
    asset_id = plan.asset_id
    db.session.delete(plan)
    db.session.commit()
    return redirect(url_for('main.ver_activo', asset_id=asset_id))
