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

    # Validación simple
    if 'usuario_id' not in data or 'item_id' not in data:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    # Simulación de validación de usuario e ítem
    if not es_usuario_valido(data['usuario_id']):
        return jsonify({"error": "El usuario no existe"}), 404
    if not es_item_valido(data['item_id']):
        return jsonify({"error": "El ítem no existe"}), 404

    # Crear el préstamo
    nuevo_prestamo = Prestamo(
        usuario_id=data['usuario_id'],
        item_id=data['item_id'],
        fecha_prestamo=datetime.now(),
        estado="pendiente"
    )
    db.session.add(nuevo_prestamo)
    db.session.commit()
    return jsonify(nuevo_prestamo.to_dict()), 201

def es_usuario_valido(usuario_id):
    # Simulación de usuarios válidos
    usuarios_validos = [1, 2, 3]
    return usuario_id in usuarios_validos

def es_item_valido(item_id):
    # Simulación de ítems válidos
    items_validos = [100, 101, 102]
    return item_id in items_validos

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
