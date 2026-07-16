from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.routes import main_routes
from app.routes import entities
from app.routes import categories
from app.routes import assets
from app.routes import maintenance_plans
from app.routes import movements
from app.routes import dashboard
