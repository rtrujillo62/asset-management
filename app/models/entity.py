from app import db
from datetime import datetime

class Entity(db.Model):
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    entity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    categories = db.relationship('Category', backref='entity', lazy=True, cascade='all, delete-orphan')
    assets = db.relationship('Asset', backref='entity', lazy=True, cascade='all, delete-orphan')
    maintenance_plans = db.relationship('MaintenancePlan', backref='entity', lazy=True, cascade='all, delete-orphan')
    movements = db.relationship('MovementLedger', backref='entity', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Entity {self.name} ({self.entity_type})>'
