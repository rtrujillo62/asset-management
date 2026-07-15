from app import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assets = db.relationship('Asset', backref='category', lazy=True, cascade='all, delete-orphan')
    maintenance_plans = db.relationship('MaintenancePlan', backref='category', lazy=True, cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('entity_id', 'name', name='unique_entity_category_name'),
    )
    
    def __repr__(self):
        return f'<Category {self.name}>'
