from flask import Flask, request, jsonify
from models import db, Prestamo
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

@app.route('/')
def hello_world():
    return "¡Hola, mundo desde Flask!"

# Ruta para obtener todos los préstamos
@app.route('/prestamos', methods=['GET'])
def obtener_prestamos():
    prestamos = Prestamo.query.all()
    return jsonify([p.to_dict() for p in prestamos])

# Ruta para crear un nuevo préstamo
@app.route('/prestamos', methods=['POST'])
def crear_prestamo():
    data = request.get_json()
    nuevo_prestamo = Prestamo(
        usuario_id=data['usuario_id'],
        item_id=data['item_id'],
        fecha_prestamo=datetime.now(),
        estado="pendiente"
    )
    db.session.add(nuevo_prestamo)
    db.session.commit()
    return jsonify(nuevo_prestamo.to_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
