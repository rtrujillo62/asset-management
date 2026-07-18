from app import db
from datetime import datetime

class EntityType(db.Model):
    """
    Catálogo de tipos de entidad (Casa, Empresa, y lo que el usuario agregue).
    """
    __tablename__ = 'entity_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<EntityType {self.name}>'
