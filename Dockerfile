# Usar la imagen de Python 3.11
FROM python:3.11-slim

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el código fuente
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 8001
EXPOSE 8001

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
