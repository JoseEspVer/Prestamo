from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Prestamo(db.Model):
    __tablename__ = 'prestamos'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    fecha_prestamo = db.Column(db.DateTime, nullable=False)
    fecha_devolucion = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=15))
    estado = db.Column(db.String(50), nullable=False, default="pendiente")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "item_id": self.item_id,
            "fecha_prestamo": self.fecha_prestamo,
            "fecha_devolucion": self.fecha_devolucion,
            "estado": self.estado
        }
