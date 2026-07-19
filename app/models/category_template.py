from app import db
from datetime import datetime

class CategoryTemplate(db.Model):
    """
    Catálogo maestro de categorías estándar (ej: Electrodomésticos,
    Equipos de Cómputo...). Se usa como plantilla al crear una entidad
    nueva, pero cada Category real queda como registro independiente
    de su entidad — editar o borrar una no afecta a las demás.
    """
    __tablename__ = 'category_templates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CategoryTemplate {self.name}>'
