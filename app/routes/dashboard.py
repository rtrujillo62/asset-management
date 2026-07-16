from flask import render_template
from app.routes import main_bp
from app.models import Entity, Category, Asset, MaintenancePlan, MovementLedger

@main_bp.route('/dashboard')
def dashboard():
    entities = Entity.query.all()
    categories = Category.query.all()
    assets = Asset.query.all()
    plans = MaintenancePlan.query.filter_by(is_active=True).all()
    
    return render_template('dashboard.html', 
        entities=entities,
        categories=categories, 
        assets=assets,
        plans=plans
    )
