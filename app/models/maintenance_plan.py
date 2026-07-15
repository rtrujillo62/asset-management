from app import db
from datetime import datetime, timedelta

class MaintenancePlan(db.Model):
    __tablename__ = 'maintenance_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Intervalo principal
    interval_type = db.Column(db.String(50), default='days')  # 'days', 'kilometers', 'hours', 'combined'
    interval_value = db.Column(db.Float, nullable=False)
    
    # Intervalo secundario (para combined)
    secondary_type = db.Column(db.String(50), nullable=True)  # 'days', 'kilometers', 'hours'
    secondary_value = db.Column(db.Float, nullable=True)
    
    estimated_cost = db.Column(db.Float)
    
    is_active = db.Column(db.Boolean, default=True)
    last_execution = db.Column(db.DateTime)
    next_due = db.Column(db.DateTime)
    last_kilometers = db.Column(db.Float)  # Último odómetro registrado
    last_hours = db.Column(db.Float)  # Últimas horas registradas
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<MaintenancePlan {self.name} - {self.interval_value} {self.interval_type}>'
    
    def calculate_next_due(self):
        """Calcula la próxima fecha vencida según el tipo de intervalo"""
        if self.interval_type == 'days':
            if self.last_execution:
                self.next_due = self.last_execution + timedelta(days=self.interval_value)
            else:
                self.next_due = datetime.utcnow() + timedelta(days=self.interval_value)
        elif self.interval_type == 'kilometers':
            # Para km, se calcula cuando se reporte el odómetro
            # next_due = last_kilometers + interval_value
            pass
        elif self.interval_type == 'hours':
            # Para horas, se calcula cuando se reporte las horas
            # next_due = last_hours + interval_value
            pass
        elif self.interval_type == 'combined':
            # Se vence cuando se alcance CUALQUIERA de los dos límites
            if self.last_execution:
                self.next_due = self.last_execution + timedelta(days=self.interval_value)
            else:
                self.next_due = datetime.utcnow() + timedelta(days=self.interval_value)
        
        return self.next_due
    
    def is_overdue(self):
        """Verifica si está vencido"""
        if not self.next_due:
            return False
        return datetime.utcnow() > self.next_due
    
    def days_until_due(self):
        """Retorna días hasta vencimiento (negativo si está vencido)"""
        if not self.next_due:
            return None
        delta = self.next_due - datetime.utcnow()
        return delta.days
    
    def get_status(self):
        """Retorna estado del plan: 'due', 'overdue', 'ok'"""
        if not self.next_due:
            return 'unknown'
        
        days_left = self.days_until_due()
        
        if days_left < 0:
            return 'overdue'
        elif days_left <= 7:  # Vence en menos de 7 días
            return 'due'
        else:
            return 'ok'
