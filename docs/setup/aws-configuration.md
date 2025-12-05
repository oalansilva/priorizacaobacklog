# Como Configurar Credenciais AWS e Bedrock

## 1. Obter Credenciais AWS

Você precisa de:
- **AWS Access Key ID**
- **AWS Secret Access Key**
- **Região AWS** (já configurada: `us-east-1`)

### Opção A: Via AWS Console (Recomendado)

1. Acesse: https://console.aws.amazon.com/iam/
2. Vá em **Users** → Seu usuário → **Security credentials**
3. Clique em **Create access key**
4. Escolha **Command Line Interface (CLI)**
5. Copie o **Access Key ID** e **Secret Access Key**

# Configurar credenciais
aws configure
```

Quando executar `aws configure`, você precisará informar:
- **AWS Access Key ID**: sua chave de acesso
- **AWS Secret Access Key**: sua chave secreta
- **Default region**: `us-east-1` (ou a região que preferir)
- **Default output format**: `json` (pode deixar padrão)

### Método 2: Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
AWS_ACCESS_KEY_ID=sua-access-key-aqui
AWS_SECRET_ACCESS_KEY=sua-secret-key-aqui
```

**⚠️ IMPORTANTE:** Nunca commite o arquivo `.env` no Git! Ele já está no `.gitignore`.

## 3. Verificar Modelos Disponíveis no Bedrock

Para ver quais modelos você tem acesso:

```bash
aws bedrock list-foundation-models --region us-east-1
```

Ou verificar modelos específicos do Anthropic:

```bash
aws bedrock list-foundation-models --region us-east-1 --query "modelSummaries[?contains(modelId, 'anthropic')]"
```

## 4. Modelos Bedrock Recomendados

Os modelos mais comuns do Anthropic Claude disponíveis:

- `us.anthropic.claude-sonnet-4-5-20250929-v1:0` (já configurado - bom custo/benefício)
- `anthropic.claude-3-haiku-20240307-v1:0` (mais rápido e barato)
- `anthropic.claude-3-opus-20240229-v1:0` (mais poderoso, mais caro)
- `anthropic.claude-3-5-sonnet-20241022-v2:0` (versão mais recente)

## 5. Habilitar Modelo no Bedrock (se necessário)

Se você receber erro de "model not found", pode ser que o modelo não esteja habilitado na sua conta:

1. Acesse: https://console.aws.amazon.com/bedrock/
2. Vá em **Model access** (ou **Foundation models**)
3. Solicite acesso aos modelos do Anthropic Claude que deseja usar
4. Aguarde aprovação (geralmente é imediato)

## 6. Testar Configuração

Depois de configurar, teste se está funcionando:

```bash
# Testar credenciais AWS
aws sts get-caller-identity

# Testar acesso ao Bedrock
aws bedrock list-foundation-models --region us-east-1 --max-results 5
```

## 7. Configuração Completa do .env

Seu arquivo `.env` deve ter algo assim:

```env
# AWS Credentials (método 2 - variáveis de ambiente)
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key

# Ou use AWS_PROFILE se preferir usar perfil do AWS CLI
# AWS_PROFILE=default

# Configurações Bedrock
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=us.anthropic.claude-sonnet-4-5-20250929-v1:0
LLM_PROVIDER=bedrock

# Configurações padrão
DEFAULT_CAPACIDADE_TOTAL=1000
DEFAULT_PERCENTUAL_SUSTENTACAO=20

# Opcionais (deixe vazio se não usar)
API_KEY_VALUE=
REDIS_URL=
STORAGE_BUCKET=
```

## 8. Alternativa: Usar OpenAI para Testes

Se não quiser configurar AWS agora, pode usar OpenAI temporariamente:

No arquivo `.env`, altere:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sua-chave-openai-aqui
```

Você já tem a `OPENAI_API_KEY` no seu `.env`, então pode testar assim primeiro!


