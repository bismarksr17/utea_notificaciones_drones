# Imagen base ligera con Python
FROM python:3.11-slim

# Establece directorio de trabajo
WORKDIR /app

# Copia dependencias e instalarlas primero (mejora caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código
COPY . .

# Comando por defecto: ejecutar el script
CMD ["python", "main.py"]