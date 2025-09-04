FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências (incluindo netcat para o script wait)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Script simples para esperar pelo PostgreSQL
RUN echo '#!/bin/bash\necho "Aguardando Postgres em db:5432..."\nuntil nc -z db 5432; do sleep 2; done\necho "Postgres está pronto!"\nexec "$@"' > /wait-for-db.sh && \
    chmod +x /wait-for-db.sh

EXPOSE 5000

CMD ["python", "run.py"]
