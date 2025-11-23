# Script para testar a API localmente

Write-Host "=== Testando API de Priorização de Backlog ===" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar se a API está rodando
Write-Host "1. Verificando se a API está rodando..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -Method GET -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ API está rodando!" -ForegroundColor Green
    Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Gray
    Write-Host "   Resposta: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API não está respondendo. Certifique-se de que está rodando:" -ForegroundColor Red
    Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""

# 2. Testar endpoint de documentação
Write-Host "2. Acesse a documentação interativa em:" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# 3. Testar priorização com CSV
Write-Host "3. Para testar com o arquivo demandas.csv:" -ForegroundColor Yellow
Write-Host "   curl -X POST `"http://localhost:8000/priorizacoes`" -F `"file=@demandas.csv`"" -ForegroundColor Cyan
Write-Host ""

# 4. Testar priorização com JSON
Write-Host "4. Para testar com JSON:" -ForegroundColor Yellow
$jsonTest = @{
    itens = @(
        @{
            item = "Projeto Teste A"
            horas = 100
            cliente = "Sim"
            negocio = "Sim"
            financeiro = "Sim"
            okr = "Sim"
        }
    )
    capacidade_total = 1000
    percentual_sustentacao = 20
} | ConvertTo-Json -Depth 10

Write-Host "   Exemplo de JSON:" -ForegroundColor Gray
Write-Host $jsonTest -ForegroundColor DarkGray
Write-Host ""

Write-Host "✅ Pronto para testar!" -ForegroundColor Green

