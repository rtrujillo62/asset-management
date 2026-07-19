from flask import render_template, abort
from app.routes import main_bp
from app.models import Entity, EntityType, Category, CategoryTemplate, Asset, MaintenancePlan, MovementLedger

@main_bp.route('/dashboard')
def dashboard():
    entities = Entity.query.order_by(Entity.name).all()
    tipos_entidad = EntityType.query.order_by(EntityType.name).all()
    return render_template(
        'dashboard.html',
        entities=entities,
        tipos_entidad=tipos_entidad,
        total_categorias=Category.query.count(),
        total_activos=Asset.query.count(),
        total_planes=MaintenancePlan.query.filter_by(is_active=True).count()
    )

@main_bp.route('/entidad/<int:entity_id>')
def ver_entidad(entity_id):
    entity = Entity.query.get(entity_id)
    if not entity:
        abort(404)
    inversion_total = sum(a.get_total_cost() for a in entity.assets)
    nombres_categorias = sorted({
        c.name for c in Category.query.with_entities(Category.name).distinct()
    })
    nombres_ya_aplicados = {c.name for c in entity.categories}
    plantillas_disponibles = [
        t for t in CategoryTemplate.query.order_by(CategoryTemplate.name).all()
        if t.name not in nombres_ya_aplicados
    ]
    return render_template(
        'entidad.html',
        entity=entity,
        inversion_total=inversion_total,
        nombres_categorias=nombres_categorias,
        plantillas_disponibles=plantillas_disponibles
    )

@main_bp.route('/categoria/<int:category_id>')
def ver_categoria(category_id):
    category = Category.query.get(category_id)
    if not category:
        abort(404)
    costo_total = sum(a.get_total_cost() for a in category.assets)
    return render_template('categoria.html', category=category, costo_total=costo_total)

@main_bp.route('/activo/<int:asset_id>')
def ver_activo(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        abort(404)
    movimientos = MovementLedger.query.filter_by(asset_id=asset.id)\
        .order_by(MovementLedger.movement_date.desc()).all()
    return render_template('activo.html', asset=asset, movimientos=movimientos)


@main_bp.route('/activo/<int:asset_id>/editar')
def editar_activo_form(asset_id):
    asset = Asset.query.get(asset_id)
    if not asset:
        abort(404)
    return render_template('editar_activo.html', asset=asset)
