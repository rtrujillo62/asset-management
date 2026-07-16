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
    interval_type = db.Column(db.String(50), default='days')   # days | kilometers | hours
    interval_value = db.Column(db.Float, nullable=False)

    # Intervalo secundario (opcional). Si existe -> plan combinado: vence lo que ocurra primero
    secondary_type = db.Column(db.String(50), nullable=True)
    secondary_value = db.Column(db.Float, nullable=True)

    estimated_cost = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)

    # Punto de partida: lecturas al momento del último mantenimiento realizado
    last_execution = db.Column(db.DateTime)
    last_kilometers = db.Column(db.Float)
    last_hours = db.Column(db.Float)
    next_due = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MaintenancePlan {self.name} - {self.interval_value} {self.interval_type}>'

    # ---------- helpers ----------

    def es_combinado(self):
        return bool(self.secondary_type and self.secondary_value)

    def usa_tipo(self, tipo):
        """True si el plan mide por 'tipo' (days/kilometers/hours), principal o secundario"""
        return self.interval_type == tipo or self.secondary_type == tipo

    def _intervalos(self):
        """Lista de (tipo, valor) que aplican a este plan"""
        pares = [(self.interval_type, self.interval_value)]
        if self.es_combinado():
            pares.append((self.secondary_type, self.secondary_value))
        return pares

    # ---------- cálculo ----------

    def calculate_next_due(self):
        """Fecha del próximo vencimiento por tiempo (solo si el plan usa días)"""
        for tipo, valor in self._intervalos():
            if tipo == 'days':
                base = self.last_execution or datetime.utcnow()
                self.next_due = base + timedelta(days=valor)
                return self.next_due
        self.next_due = None
        return None

    def objetivo(self, tipo):
        """Valor meta para el próximo mantenimiento en ese tipo de medida"""
        for t, valor in self._intervalos():
            if t != tipo:
                continue
            if tipo == 'kilometers':
                return (self.last_kilometers or 0) + valor
            if tipo == 'hours':
                return (self.last_hours or 0) + valor
            if tipo == 'days':
                base = self.last_execution or self.created_at or datetime.utcnow()
                return base + timedelta(days=valor)
        return None

    def evaluar(self):
        """
        Evalúa cada intervalo contra la lectura actual del activo.
        Devuelve lista de dicts: tipo, objetivo, restante, estado.
        restante < 0  -> vencido
        """
        resultados = []
        activo = self.asset

        for tipo, _valor in self._intervalos():
            objetivo = self.objetivo(tipo)
            if objetivo is None:
                continue

            if tipo == 'days':
                restante = (objetivo - datetime.utcnow()).days
                umbral = 7
            elif tipo == 'kilometers':
                actual = (activo.current_kilometers if activo else None)
                if actual is None:
                    resultados.append({'tipo': tipo, 'objetivo': objetivo,
                                       'restante': None, 'estado': 'sin_lectura'})
                    continue
                restante = objetivo - actual
                umbral = 500
            elif tipo == 'hours':
                actual = (activo.current_hours if activo else None)
                if actual is None:
                    resultados.append({'tipo': tipo, 'objetivo': objetivo,
                                       'restante': None, 'estado': 'sin_lectura'})
                    continue
                restante = objetivo - actual
                umbral = 20
            else:
                continue

            if restante < 0:
                estado = 'overdue'
            elif restante <= umbral:
                estado = 'due'
            else:
                estado = 'ok'

            resultados.append({'tipo': tipo, 'objetivo': objetivo,
                               'restante': restante, 'estado': estado})
        return resultados

    def get_status(self):
        """Estado global: gana el peor (lo que ocurra primero)"""
        evaluaciones = self.evaluar()
        if not evaluaciones:
            return 'unknown'
        estados = [e['estado'] for e in evaluaciones]
        if 'overdue' in estados:
            return 'overdue'
        if 'due' in estados:
            return 'due'
        if 'ok' in estados:
            return 'ok'
        return 'sin_lectura'

    def is_overdue(self):
        return self.get_status() == 'overdue'

    def days_until_due(self):
        for e in self.evaluar():
            if e['tipo'] == 'days':
                return e['restante']
        return None

    def registrar_ejecucion(self, fecha=None):
        """
        Marca el mantenimiento como realizado HOY, tomando como punto de partida
        las lecturas actuales del activo. El próximo se calcula desde aquí.
        """
        self.last_execution = fecha or datetime.utcnow()
        if self.asset:
            if self.usa_tipo('kilometers'):
                self.last_kilometers = self.asset.current_kilometers or 0
            if self.usa_tipo('hours'):
                self.last_hours = self.asset.current_hours or 0
        self.calculate_next_due()
