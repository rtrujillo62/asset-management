from flask import render_template, request, redirect, url_for
from app.routes import main_bp
from app import db
from app.models import EntityType, Category

@main_bp.route('/catalogos')
def catalogos():
    tipos = EntityType.query.order_by(EntityType.name).all()
    # Nombres de categoría ya usados en cualquier entidad, sin repetir
    nombres_categorias = sorted({
        c.name for c in Category.query.with_entities(Category.name).distinct()
    })
    return render_template('catalogos.html', tipos=tipos, nombres_categorias=nombres_categorias)

@main_bp.route('/catalogos/tipos', methods=['POST'])
def crear_tipo_entidad():
    nombre = (request.form.get('name') or '').strip()
    if nombre and not EntityType.query.filter_by(name=nombre).first():
        db.session.add(EntityType(name=nombre))
        db.session.commit()
    return redirect(url_for('main.catalogos'))

@main_bp.route('/catalogos/tipos/<int:tipo_id>/eliminar', methods=['POST'])
def eliminar_tipo_entidad(tipo_id):
    tipo = EntityType.query.get(tipo_id)
    if tipo:
        db.session.delete(tipo)
        db.session.commit()
    return redirect(url_for('main.catalogos'))
