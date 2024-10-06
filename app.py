from flask import Flask, request, jsonify, redirect
from models import db, Prestamo
from config import Config
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos
db.init_app(app)

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Ruta para obtener todos los préstamos
@app.route('/prestamos', methods=['GET'])
def obtener_prestamos():
    prestamos = Prestamo.query.all()
    return jsonify([p.to_dict() for p in prestamos])

# Ruta para crear un nuevo préstamo
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

    nuevo_prestamo = Prestamo(
        usuario_id=data['usuario_id'],
        item_id=data['item_id'],
        fecha_prestamo=datetime.now(),
        estado="pendiente"
    )
    db.session.add(nuevo_prestamo)
    db.session.commit()
    return jsonify(nuevo_prestamo.to_dict()), 201

@app.route('/prestamos/<int:id>', methods=['DELETE'])
def eliminar_prestamo(id):
    prestamo = Prestamo.query.get(id)

    if not prestamo:
        return jsonify({"error": "Préstamo no encontrado"}), 404

    db.session.delete(prestamo)
    db.session.commit()
    return jsonify({"mensaje": "Préstamo eliminado"}), 200

# Funciones adicionales
def es_usuario_valido(usuario_id):
    url = f"http://ip_del_servicio_de_usuarios:puerto/{usuario_id}"
    response = request.get(url)
    return response.status_code == 200

def es_item_valido(item_id):
    url = f"http://ip_del_servicio_de_usuarios:puerto/{item_id}"
    response = request.get(url)
    return response.status_code == 200

def reducir_stock(item_id):
    url = f"http://ip_del_servicio_de_stock:puerto/libros/{item_id}/reducir"
    response = request.post(url)
    return response.status_code == 200

def tiene_sancion(usuario_id):
    url = f"http://ip_del_servicio_de_sanciones:puerto/validate/{usuario_id}"
    response = request.get(url)
    return response.status_code == 200 and response.json().get('sancionado')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004)
