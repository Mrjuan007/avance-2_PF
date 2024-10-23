# Usa la imagen base de la última versión de Python
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Actualiza pip e instala las dependencias necesarias desde requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el archivo de código Python al contenedor
COPY ./app_dash.py .

# Copia el archivo CSV al contenedor
COPY ./26-09-2022.txt .

# Expone el puerto 8050 en el contenedor
EXPOSE 8050

# Ejecuta el script de Python
CMD ["python", "app_dash.py"]



