from flask import Flask, request, jsonify, redirect
from models import db, Prestamo, SolicitudLibro  # Importar la nueva entidad SolicitudLibro
from config import Config
from datetime import datetime
import requests  # Para manejar las solicitudes a los servicios externos
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
app.config.from_object(Config)
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
)

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def swagger():
    return redirect('/swagger')

@app.route('/api/prestamos', methods=['GET'])
def obtener_prestamos():
    prestamos = Prestamo.query.all()
    return jsonify([p.to_dict() for p in prestamos])

@app.route('/api/prestamos', methods=['POST'])
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

@app.route('/api/prestamos/<int:prestamo_id>/devolver', methods=['PUT'])
def devolver_prestamo(prestamo_id):
    prestamo = Prestamo.query.get_or_404(prestamo_id)
    
    if prestamo.estado == "devuelto":
        return jsonify({"error": "El préstamo ya fue devuelto"}), 400

    if modificar_stock(prestamo.item_id, "incrementar"):
        prestamo.estado = "devuelto"
        db.session.commit()

        # Al devolver el libro, revisa si hay solicitudes pendientes
        prestamo_asignado = asignar_prestamo_a_solicitud(prestamo.item_id)
        if prestamo_asignado:
            return jsonify({
                "mensaje": "Préstamo devuelto y nuevo préstamo asignado a una solicitud urgente",
                "prestamo_asignado": prestamo_asignado
            }), 200
        else:
            return jsonify({"mensaje": "Préstamo devuelto, no hay solicitudes pendientes"}), 200
    else:
        return jsonify({"error": "No se pudo incrementar el stock"}), 500




@app.route('/api/solicitudes', methods=['GET'])
def obtener_solicitudes():
    solicitudes = SolicitudLibro.query.all()
    return jsonify([s.to_dict() for s in solicitudes])

@app.route('/api/solicitudes', methods=['POST'])
def crear_solicitud():
    data = request.get_json()

    if 'usuario_id' not in data or 'libro_id' not in data or 'carrera' not in data:
        return jsonify({"error": "Faltan campos requeridos"}), 400

    nueva_solicitud = SolicitudLibro(
        usuario_id=data['usuario_id'],
        libro_id=data['libro_id'],

        es_urgente=data.get('es_urgente', False),
        fecha_solicitud=datetime.now()
    )

    db.session.add(nueva_solicitud)
    db.session.commit()
    return jsonify(nueva_solicitud.to_dict()), 201



def asignar_prestamo_a_solicitud(libro_id):
    solicitudes = SolicitudLibro.query.filter_by(libro_id=libro_id).order_by(
        SolicitudLibro.es_urgente.desc(),
        SolicitudLibro.fecha_solicitud.asc()
    ).all()

    if not solicitudes:
        return None

    solicitud = solicitudes[0] 

    nuevo_prestamo = Prestamo(
        usuario_id=solicitud.usuario_id,
        item_id=solicitud.libro_id,
        fecha_prestamo=datetime.now(),
        estado="pendiente",
        solicitud_id=solicitud.id
    )

    if modificar_stock(solicitud.libro_id, "reducir"):
        db.session.add(nuevo_prestamo)
        db.session.delete(solicitud) 
        db.session.commit()
        return nuevo_prestamo.to_dict()
    else:
        return None



def es_item_valido(item_id):
    url = f"http://spring-app:8080/api/inventario/{item_id}"
    response = requests.get(url)
    return response.status_code == 200

def verificar_disponibilidad_item(item_id):
    url = f"http://spring-app:8080/api/inventario/{item_id}/stock"
    response = requests.get(url)
    if response.status_code == 200:
        stock = response.json()
        return stock > 0
    return False

def modificar_stock(item_id, accion):
    url = f"http://spring-app:8080/api/inventario/{item_id}/modificar-stock"
    response = requests.put(url, params={'accion': accion})
    return response.status_code == 200

def es_usuario_valido(usuario_id):
    url = f"http://gestionusuarioservice:5001/api/User/{usuario_id}"
    response = requests.get(url)
    return response.status_code == 200

def tiene_sancion(usuario_id):
    url = f"http://gestionusuarioservice:5001/api/validate/{usuario_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return True
    return False

app.register_blueprint(swaggerui_blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004)
