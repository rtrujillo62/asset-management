from app import db
from datetime import datetime

class Asset(db.Model):
    __tablename__ = 'assets'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(255))
    model = db.Column(db.String(255))
    serial_number = db.Column(db.String(255), unique=True, nullable=True)
    
    purchase_date = db.Column(db.DateTime, nullable=False)
    purchase_price = db.Column(db.Float)
    warranty_expiry = db.Column(db.DateTime)
    
    requires_maintenance = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    movements = db.relationship('MovementLedger', backref='asset', lazy=True, cascade='all, delete-orphan')
    maintenance_plans = db.relationship('MaintenancePlan', backref='asset', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Asset {self.name} ({self.brand} {self.model})>'
    
    def get_total_cost(self):
        return sum(m.amount for m in self.movements if m.amount)
    
    def get_warranty_status(self):
        if not self.warranty_expiry:
            return None
        return datetime.utcnow() < self.warranty_expiry
