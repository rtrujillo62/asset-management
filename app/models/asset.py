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
    year = db.Column(db.Integer)
    serial_number = db.Column(db.String(255), unique=True, nullable=True)

    purchase_date = db.Column(db.DateTime, nullable=True)
    purchase_price = db.Column(db.Float)
    warranty_expiry = db.Column(db.DateTime)

    requires_maintenance = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')

    # Lecturas actuales del activo (odómetro / horómetro)
    current_kilometers = db.Column(db.Float)
    current_hours = db.Column(db.Float)
    last_reading_date = db.Column(db.DateTime)

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

    def usa_kilometros(self):
        """True si algún plan de este activo se mide por kilómetros"""
        return any(p.usa_tipo('kilometers') for p in self.maintenance_plans if p.is_active)

    def usa_horas(self):
        """True si algún plan de este activo se mide por horas"""
        return any(p.usa_tipo('hours') for p in self.maintenance_plans if p.is_active)
