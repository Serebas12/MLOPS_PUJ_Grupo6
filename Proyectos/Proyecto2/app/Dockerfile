# Imagen de python
FROM python:3.9-slim

# Directorio a trabajat
WORKDIR /app

# Copia e instalación de requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia todo el contenido
COPY . .

# Expone puerto
EXPOSE 8989

# Inicio del api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8989"]