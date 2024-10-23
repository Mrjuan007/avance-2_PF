# Usa la imagen base de la última versión de Python
FROM python:3.12-slim

# Instala las herramientas de compilación y dependencias necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libatlas-base-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt .

# Actualiza pip e instala las dependencias necesarias desde requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia el archivo de código Python al contenedor
COPY ./app_dash.py .

# Copia los archivos CSV al contenedor
COPY ./archivo_parte_1.csv .
COPY ./archivo_parte_2.csv .
COPY ./archivo_parte_3.csv .

# Expone el puerto 8050 en el contenedor
EXPOSE 8050

# Ejecuta el script de Python
CMD ["python", "app_dash.py"]
