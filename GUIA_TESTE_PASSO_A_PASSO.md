# Guia Passo a Passo de Teste (Atualizado)

Este guia fornece instruções detalhadas para testar o sistema de processamento de operações FIDC.

## 1. EXECUTAR O SISTEMA

Certifique-se de que o Docker está instalado e em execução, então execute:

```bash
docker compose down -v        # Limpa qualquer instância anterior
docker compose build --no-cache  # Reconstrói os containers
docker compose up             # Inicia todos os serviços
```

Aguarde até ver mensagens indicando que todos os serviços estão rodando:
- API: "Running on http://0.0.0.0:5000"
- Worker: "celery@xxxx ready"
- MinIO e banco de dados também inicializados

## 2. TESTAR ENDPOINT DE STATUS

Este é um teste simples para verificar se a API está respondendo:

```bash
curl http://localhost:5000/jobs/test/status
```

Você deve ver uma resposta JSON com status "ok" e um timestamp.

## 3. ENVIAR OPERAÇÕES PARA PROCESSAMENTO

Envie algumas operações de compra e venda para processamento:

```bash
curl -X POST http://localhost:5000/operations/process \
  -H "Content-Type: application/json" \
  -d '{
    "fidc_id": "FIDC001",
    "operations": [
      {
        "id": "op_001",
        "asset_code": "PETR4",
        "operation_type": "BUY",
        "quantity": 1000,
        "operation_date": "2025-09-01"
      },
      {
        "id": "op_002",
        "asset_code": "VALE3",
        "operation_type": "SELL",
        "quantity": 500,
        "operation_date": "2025-09-01"
      }
    ]
  }'
```

A resposta incluirá um `job_id` que você usará para acompanhar o status do processamento.

## 4. VERIFICAR STATUS DO JOB

Use o ID do job retornado para verificar o status:

```bash
curl http://localhost:5000/jobs/SEU_JOB_ID_AQUI/status
```

O status será atualizado à medida que as operações são processadas:
- PROCESSING: ainda em processamento
- COMPLETED: todas as operações foram processadas

Você também verá estatísticas como o número de operações processadas e com falha.

## 5. ENVIAR MAIS OPERAÇÕES (OPCIONAL)

Você pode enviar mais operações para o mesmo FIDC:

```bash
curl -X POST http://localhost:5000/operations/process \
  -H "Content-Type: application/json" \
  -d '{
    "fidc_id": "FIDC001",
    "operations": [
      {
        "id": "op_003",
        "asset_code": "ITUB4",
        "operation_type": "BUY",
        "quantity": 2000,
        "operation_date": "2025-09-02"
      },
      {
        "id": "op_004",
        "asset_code": "MGLU3",
        "operation_type": "SELL",
        "quantity": 3000,
        "operation_date": "2025-09-02"
      }
    ]
  }'
```

## 6. EXPORTAR OPERAÇÕES PARA CSV

Quando as operações tiverem sido processadas, você pode exportá-las para CSV:

```bash
curl -X POST http://localhost:5000/operations/export \
  -H "Content-Type: application/json" \
  -d '{
    "fidc_id": "FIDC001",
    "start_date": "2025-09-01",
    "end_date": "2025-09-30"
  }'
```

A resposta incluirá uma URL para baixar o arquivo CSV.

## 7. BAIXAR O ARQUIVO EXPORTADO

### Opção 1: Interface Web do MinIO

1. Abra o navegador e acesse: http://localhost:9001
2. Faça login com:
   - Username: minioadmin
   - Password: minioadmin
3. Navegue até o bucket "fidc-exports"
4. Encontre a pasta com o ID do seu FIDC (ex: "FIDC001")
5. Clique no arquivo CSV para baixá-lo

### Opção 2: URL Direta (Navegador)

Acesse a URL retornada pela API no passo anterior em seu navegador. Certifique-se de substituir "minio:9000" por "localhost:9000" se necessário.

## 8. VERIFICAR LOGS EM CASO DE PROBLEMAS

Se algo não funcionar como esperado, verifique os logs:

```bash
# Ver logs da API
docker compose logs api

# Ver logs do worker
docker compose logs worker

# Ver logs contínuos (seguir)
docker compose logs -f
```

## SOLUÇÃO DE PROBLEMAS COMUNS

| Situação | O que fazer |
|----------|-------------|
| API não responde | Verifique se o docker compose up ainda está rodando |
| Erro de "rate limit" | Aguarde e consulte o status novamente (simulamos limitação de API) |
| Job não sai de PROCESSING | Verifique os logs: `docker compose logs -f worker` |
| Link de download não abre | Verifique se o MinIO está no ar (http://localhost:9001) |
| Arquivo não aparece | Confirme que as operações foram COMPLETED antes do export |

## LIMPAR TUDO AO FINAL

Para desligar todos os serviços e remover volumes:

```bash
# Pressione Ctrl + C no terminal onde está rodando
docker compose down -v
```

## RESUMO RÁPIDO

1. `docker compose up`
2. Enviar POST /operations/process
3. Acompanhar GET /jobs/<id>/status
4. Fazer export /operations/export
5. Baixar arquivo via console MinIO (http://localhost:9001)
