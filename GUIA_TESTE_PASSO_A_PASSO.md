# Guia Passo a Passo (Pessoa Leiga)

Este guia ensina como subir o sistema, rodar operações e gerar um arquivo de exportação.
Você só precisa seguir as instruções exatamente como estão.

---

## 1. O QUE VOCÊ VAI USAR

- Aplicativo "Docker Desktop" (já instalado)
- Navegador (Chrome, Edge ou similar)
- Visual Studio Code (VS Code)
- Terminal (PowerShell no Windows)
- (Opcional) Postman para testar requisições. Se não tiver, usaremos comandos prontos.

---

## 2. ABRIR O PROJETO

1. Abra o Visual Studio Code.
2. Clique em "File" > "Open Folder".
3. Selecione a pasta:
   c:\Users\PedroHenriqueMussoli\Documents\Projetos\Desafio_ZRP\desafio-zrp

---

## 3. CONFERIR SE O DOCKER ESTÁ LIGADO

1. Abra o aplicativo "Docker Desktop".
2. Aguarde até aparecer “Running” ou um ícone verde.
3. Não feche o Docker enquanto testa.

---

## 4. CRIAR O ARQUIVO .env

1. No VS Code, no Explorador (sidebar à esquerda) localize o arquivo: `.env.example`.
2. Clique com o botão direito nele e escolha: "Copy".
3. Clique em uma área vazia e selecione "Paste".
4. Renomeie o arquivo copiado para: `.env`
   (Se o Windows perguntar sobre extensões, confirme.)

Não altere nada dentro do arquivo por enquanto.

---

## 5. SUBIR O SISTEMA (TODOS OS SERVIÇOS)

1. Abra o Terminal do VS Code:
   Menu "Terminal" > "New Terminal".
2. Verifique se o caminho atual é a pasta do projeto (deve mostrar ...\desafio-zrp).
3. Digite (ou copie e cole) e pressione Enter:

```
docker compose up --build
```

4. Espere. A primeira vez pode demorar (download de imagens).
5. Aguarde até ver mensagens como:
   - “Application running on http://0.0.0.0:5000”
   - Worker Celery com linhas contendo “ready” ou tarefas sendo executadas.

Não feche este terminal enquanto testar.

---

## 6. ABRIR UMA NOVA JANELA PARA TESTAR COMANDOS

1. No VS Code abra um novo terminal:
   Terminal > New Terminal.
2. Este novo terminal será usado para enviar comandos (sem parar os containers).

---

## 7. TESTAR SE A API ESTÁ NO AR

No novo terminal digite:

```
curl http://localhost:5000/jobs/testando/status
```

Resposta esperada (parecido com):

```
{"error":"Job not found"}
```

Se apareceu algo assim, a API está funcionando.

---

## 8. CRIAR UM CONJUNTO DE OPERAÇÕES (PROCESSO 1)

Envie uma operação simples (compra):

```
curl -X POST http://localhost:5000/operations/process ^
  -H "Content-Type: application/json" ^
  -d "{\"fidc_id\":\"FIDC001\",\"operations\":[{\"id\":\"op_001\",\"asset_code\":\"PETR4\",\"operation_type\":\"BUY\",\"quantity\":1000,\"operation_date\":\"2024-09-01\"}]}"
```

Resposta esperada:

```
{"job_id":"<um código grande aqui>","status":"ENQUEUED"}
```

Copie o valor de job_id (sem aspas).

---

## 9. CONSULTAR STATUS DO PROCESSAMENTO

Troque abaixo <JOB_ID_AQUI> pelo que você copiou:

```
curl http://localhost:5000/jobs/<JOB_ID_AQUI>/status
```

Enquanto processa pode aparecer:

```
{"job_id":"...","status":"PROCESSING","total_operations":1,"processed":0,"failed":0,"estimated_completion":null}
```

Depois de alguns segundos:

```
{"job_id":"...","status":"COMPLETED","total_operations":1,"processed":1,"failed":0,"estimated_completion":null}
```

---

## 10. ENVIAR UM LOTE MAIOR (COM COMPRA E VENDA)

```
curl -X POST http://localhost:5000/operations/process ^
  -H "Content-Type: application/json" ^
  -d "{\"fidc_id\":\"FIDC001\",\"operations\":[
    {\"id\":\"op_002\",\"asset_code\":\"VALE3\",\"operation_type\":\"BUY\",\"quantity\":500,\"operation_date\":\"2024-09-02\"},
    {\"id\":\"op_003\",\"asset_code\":\"PETR4\",\"operation_type\":\"SELL\",\"quantity\":300,\"operation_date\":\"2024-09-02\"},
    {\"id\":\"op_004\",\"asset_code\":\"ITUB4\",\"operation_type\":\"BUY\",\"quantity\":200,\"operation_date\":\"2024-09-03\"}
  ]}"
```

Guarde o job_id retornado e acompanhe como antes.

---

## 11. VERIFICAR O DINHEIRO DO FUNDO (OPCIONAL)

1. No terminal digite:

```
docker compose exec db psql -U fidc -d fidc -c "select fidc_id, available_cash from fidc_cash;"
```

2. Deve mostrar uma linha com FIDC001 e um valor ajustado (diminui após BUY, aumenta após SELL).

---

## 12. GERAR EXPORTAÇÃO (CRIAR ARQUIVO NO MINIO)

Quando as operações tiverem status COMPLETED:

```
curl -X POST http://localhost:5000/operations/export ^
  -H "Content-Type: application/json" ^
  -d "{\"fidc_id\":\"FIDC001\",\"start_date\":\"2024-09-01\",\"end_date\":\"2024-09-30\"}"
```

Resposta esperada (exemplo):

```
{
  "filename":"FIDC001/export_FIDC001_20240901T153000.csv",
  "rows":4,
  "download_url":"http://localhost:9000/fidc-exports/FIDC001/export_FIDC001_20240901T153000.csv?X-Amz-Algorithm=..."
}
```

Copie o link de download (download_url) e abra no navegador para baixar o CSV.

---

## 13. ABRIR O CONSOLE DO MINIO (ARQUIVOS)

1. Abra no navegador:
   http://localhost:9001
2. Login:
   Usuário: minioadmin
   Senha: minioadmin
3. Clique no bucket: fidc-exports
4. Abra a pasta FIDC001 e veja o arquivo exportado (CSV).

---

## 14. RODAR TESTES AUTOMÁTICOS (OPCIONAL)

No terminal:

```
docker compose run --rm api pytest -q
```

Se aparecer algo como "1 passed", está ok.

---

## 15. SE ACONTECER ALGUM ERRO

| Situação | O que fazer |
|----------|-------------|
| API não responde | Ver se docker compose up ainda está rodando |
| Erro de “rate limit” | Só esperar e consultar status novamente |
| Job não sai de PROCESSING | Ver logs: `docker compose logs -f worker` |
| Link de download não abre | Ver se MinIO está no ar (http://localhost:9001) |
| Arquivo não aparece | Confirmar que operações foram COMPLETED antes do export |

---

## 16. LIMPAR TUDO AO FINAL

Se quiser desligar tudo e remover volumes:

```
Ctrl + C (no terminal onde está rodando)
docker compose down -v
```

---

## 17. RESUMO RÁPIDO

1. docker compose up --build
2. Enviar POST /operations/process
3. Acompanhar GET /jobs/<id>/status
4. Fazer export /operations/export
5. Baixar arquivo no link ou via console MinIO

Pronto.

---

## 18. PROBLEMAS COMUNS

| Mensagem / Sintoma | Causa | Solução |
|--------------------|-------|---------|
| /wait-db.sh: nc: not found | netcat não instalado | Rebuild após ajustar Dockerfile (ver correção) |
| Fica em "Aguardando Postgres..." | Banco ainda iniciando | Aguardar alguns segundos |
| Connection refused Redis | Redis não subiu | docker compose logs redis |
| Rate limit exceeded | Muitas requisições de preço no minuto | Aguardar 60s e consultar status novamente |
| Job parado em PROCESSING | Retries em andamento | Ver logs do worker |
| Export sem linhas | Operações não COMPLETED | Conferir status das operações pelo job |

Rebuild completo:
1. docker compose down
2. docker compose build --no-cache
3. docker compose up
