from app import db
from datetime import datetime

class MovementLedger(db.Model):
    __tablename__ = 'movement_ledger'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    
    movement_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)
    movement_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    maintenance_plan = db.relationship('MaintenancePlan', backref='movements')
    
    def __repr__(self):
        return f'<Movement {self.movement_type} - ${self.amount}>'
    
    @staticmethod
    def get_asset_total(asset_id):
        return db.session.query(db.func.sum(MovementLedger.amount)).filter_by(asset_id=asset_id).scalar() or 0
    
    @staticmethod
    def get_asset_by_type(asset_id, movement_type):
        return db.session.query(db.func.sum(MovementLedger.amount)).filter_by(
            asset_id=asset_id,
            movement_type=movement_type
        ).scalar() or 0
