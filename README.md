# FIDC Operations API

## Visão Geral
API RESTful para processamento de operações FIDC, com processamento assíncrono (Celery), integração simulada de preços, cálculo de operações, monitoramento de jobs e exportação de dados para MinIO.

## Tecnologias
- Python, Flask
- Celery (assíncrono)
- PostgreSQL
- Redis
- MinIO (S3 compatível)
- Docker e Docker Compose

## Estrutura do Projeto
```
├── app
│   ├── api
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── endpoints/
│   ├── models
│   │   ├── __init__.py
│   │   ├── fidc_cash.py
│   │   ├── job.py
│   │   ├── operation.py
│   ├── services
│   │   ├── calculation_service.py
│   │   ├── export_service.py
│   │   ├── job_service.py
│   │   ├── operation_service.py
│   │   ├── price_service.py
│   ├── tasks
│   │   ├── operation_tasks.py
│   │   ├── export_tasks.py
│   └── utils
├── migrations
├── tests
│   ├── unit
│   └── integration
├── celery_worker.py
├── run.py
├── requirements.txt
├── .env.example
├── .env
├── docker-compose.yml
├── Dockerfile
├── GUIA_TESTE_PASSO_A_PASSO.md
├── README.md
```

## Como Executar

1. **Configurar ambiente**
   - Instale Docker Desktop
   - Copie `.env.example` para `.env` e ajuste se necessário

2. **Subir os serviços**
   ```powershell
   docker compose build --no-cache
   docker compose up
   ```
   - API: http://localhost:5000
   - MinIO: http://localhost:9001 (minioadmin/minioadmin)

## Principais Endpoints

### Processar operações
```http
POST /operations/process
```
Payload:
```json
{
  "fidc_id": "FIDC001",
  "operations": [
    {
      "id": "op_001",
      "asset_code": "PETR4",
      "operation_type": "BUY",
      "quantity": 1000,
      "operation_date": "2024-09-01"
    }
  ]
}
```

### Consultar status do job
```http
GET /jobs/<job_id>/status
```

### Exportar operações para CSV (MinIO)
```http
POST /operations/export
```
Payload:
```json
{
  "fidc_id": "FIDC001",
  "start_date": "2024-09-01",
  "end_date": "2024-09-30"
}
```

## Testes
```powershell
pytest
```

## Guia de Teste
Consulte o arquivo `GUIA_TESTE_PASSO_A_PASSO.md` para um passo a passo detalhado de uso e validação.

## Solução de Problemas
- Se a URL de download do MinIO vier como `minio:9000`, troque por `localhost:9000` no navegador.
- Use o console do MinIO para baixar arquivos: http://localhost:9001
- Consulte logs com `docker compose logs api` ou `docker compose logs worker`

## Licença
MIT License
