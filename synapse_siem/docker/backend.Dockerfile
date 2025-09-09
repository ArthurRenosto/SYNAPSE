# Use Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o projeto
COPY . .

# Exponha porta
EXPOSE 8000

# Comando para rodar o Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]