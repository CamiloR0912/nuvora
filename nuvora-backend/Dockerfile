FROM python:3.11-slim

WORKDIR /app

# Copiar archivo de dependencias
COPY requierements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requierements.txt

# Copiar todo el código del backend
COPY . .

# Exponer el puerto 8000
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]