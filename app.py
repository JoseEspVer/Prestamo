from flask import Flask, request, jsonify
from models import db, Prestamo
from config import Config
from datetime import datetime
import requests  # Para manejar las solicitudes a los servicios externos

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/prestamos', methods=['GET'])
def obtener_prestamos():
    prestamos = Prestamo.query.all()
    return jsonify([p.to_dict() for p in prestamos])

@app.route('/prestamos', methods=['POST'])
def crear_prestamo():
    data = request.get_json()

    if 'usuario_id' not in data or 'item_id' not in data:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    if not es_usuario_valido(data['usuario_id']):
        return jsonify({"error": "El usuario no existe"}), 404
    if not es_item_valido(data['item_id']):
        return jsonify({"error": "El ítem no existe"}), 404
    if tiene_sancion(data['usuario_id']):
        return jsonify({"error": "El usuario tiene sanciones"}), 403

    if not verificar_disponibilidad_item(data['item_id']):
        return jsonify({"error": "No hay stock disponible"}), 400

    nuevo_prestamo = Prestamo(
        usuario_id=data['usuario_id'],
        item_id=data['item_id'],
        fecha_prestamo=datetime.now(),
        estado="pendiente"
    )

    if modificar_stock(data['item_id'], "reducir"):
        db.session.add(nuevo_prestamo)
        db.session.commit()
        return jsonify(nuevo_prestamo.to_dict()), 201
    else:
        return jsonify({"error": "No se pudo reducir el stock"}), 500

def es_item_valido(item_id):
    # Usamos el nombre del contenedor 'spring_app' y el puerto 8080
    url = f"http://spring_app:8080/{item_id}"
    response = requests.get(url)
    return response.status_code == 200

def verificar_disponibilidad_item(item_id):
    # Usamos el nombre del contenedor 'spring_app' y el puerto 8080
    url = f"http://spring_app:8080/{item_id}/stock"
    response = requests.get(url)
    if response.status_code == 200:
        stock = response.json()
        return stock > 0
    return False

def modificar_stock(item_id, accion):
    # Usamos el nombre del contenedor 'spring_app' y el puerto 8080
    url = f"http://spring_app:8080/{item_id}/modificar-stock"
    response = requests.put(url, params={'accion': accion})
    return response.status_code == 200

def es_usuario_valido(usuario_id):
    # Usamos el nombre del contenedor 'gestionusuario_service' y el puerto 8081
    url = f"http://gestionusuario_service:8081/{usuario_id}"
    response = requests.get(url)
    return response.status_code == 200

def tiene_sancion(usuario_id):
    url = f"http://gestionusuario_service:8081/validate/{usuario_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    return False

@app.route('/prestamos/<int:prestamo_id>/devolver', methods=['PUT'])
def devolver_prestamo(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    if prestamo.estado == "devuelto":
        return jsonify({"error": "El préstamo ya fue devuelto"}), 400

    if modificar_stock(prestamo.item_id, "incrementar"):
        prestamo.estado = "devuelto"
        db.session.commit()
        return jsonify(prestamo.to_dict()), 200
    else:
        return jsonify({"error": "No se pudo incrementar el stock"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004)
