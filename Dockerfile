FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Script simples wait
RUN printf '#!/bin/sh\nset -e\nhost=$1\nshift\nuntil nc -z $host 5432; do echo "Aguardando Postgres..."; sleep 2; done\nexec "$@"\n' > /wait-db.sh && chmod +x /wait-db.sh

EXPOSE 5000

CMD ["python", "run.py"]