# 🚀 Como Testar em Produção

Sua API está implantada e pronta para uso!

**URL da API:** `https://z1fbg1nm87.execute-api.us-east-1.amazonaws.com/prod/priorizacoes`

## 1. Atualize a Lambda (Último Passo)

Acabei de enviar uma correção para suportar colunas como "Esforço Estimado" no CSV.

1. Vá na sua função Lambda: [PriorizaBacklogAPI](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/PriorizaBacklogAPI)
2. Aba **Code** -> **Image** -> **Deploy new image**
3. Selecione a imagem mais recente (`latest`) e salve.

## 2. Prepare o Arquivo de Teste

Já criei um arquivo `exemplo_backlog.csv` na pasta do projeto com o seguinte conteúdo:

```csv
ID;Titulo;Descricao;Valor de Negocio;Esforco Estimado;Area;Dependencias;Prazo
1;Login SSO;Implementar login único;Alto;13;Segurança;;2025-12-01
2;Relatório Financeiro;Criar relatório mensal;Médio;8;Financeiro;;2025-11-15
3;Correção Bug X;Corrigir erro na tela Y;Baixo;3;Sustentação;;
```

## 3. Execute o Teste (PowerShell)

Abra o PowerShell na pasta do projeto e execute:

```powershell
curl.exe -X POST "https://z1fbg1nm87.execute-api.us-east-1.amazonaws.com/prod/priorizacoes" `
  -F "file=@exemplo_backlog.csv" `
  -F "capacidade_total=100" `
  -F "percentual_sustentacao=20"
```

## 4. Resultado Esperado

Você receberá um JSON com a lista priorizada e um link para o Excel gerado (se configurado S3, senão apenas o JSON).

Exemplo de resposta:
```json
{
  "capacidade_iniciativas": 80.0,
  "horas_alocadas": 21.0,
  "itens": [
    {
      "prioridade": 1,
      "item": "Login SSO",
      "horas": 13.0,
      "justificativa": "Alto valor de negócio e segurança...",
      "status": "Priorizado"
    },
    ...
  ]
}
```
