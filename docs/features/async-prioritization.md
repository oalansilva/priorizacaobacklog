# Priorização Assíncrona

## 🎯 Objetivo

Resolver o problema de timeouts do API Gateway (limite de 30 segundos) durante o processo de priorização, que pode levar mais tempo devido à complexidade das chamadas ao AWS Bedrock.

## 🏗️ Arquitetura

O sistema utiliza um modelo de execução assíncrona baseado em **Python Threading** dentro do ambiente Lambda, combinado com persistência de estado no **DynamoDB**.

### Fluxo de Execução

1.  **Solicitação**: O usuário solicita a priorização via Chat.
2.  **Agente**: O agente chama a ferramenta `prioritize_backlog`.
3.  **Threading**: A ferramenta inicia uma **thread em background** (daemon) para executar a lógica pesada de priorização.
4.  **Resposta Imediata**: A ferramenta retorna imediatamente uma mensagem de confirmação ("Priorização iniciada...") para o usuário, evitando o timeout.
5.  **Processamento**: A thread em background processa os itens, chama o Bedrock e atualiza o banco de dados.
6.  **Estado**: Durante todo o processo, o status é salvo na tabela `SystemSettings` do DynamoDB.

## 📊 Gerenciamento de Estado

O estado da priorização é armazenado no DynamoDB com os seguintes campos:

-   `last_prioritization_status`: Estado atual (`running`, `completed`, `error`).
-   `last_prioritization_time`: Timestamp da última execução.
-   `last_prioritization_message`: Mensagem de resultado ou erro.

### Estados Possíveis

-   **running**: Processo em andamento. O frontend exibe um spinner amarelo.
-   **completed**: Processo finalizado com sucesso. O frontend exibe um banner verde com a data.
-   **error**: Falha no processo. O frontend exibe um banner vermelho com o erro.

## 📱 Interface do Usuário

### Backlog Board
O componente `BacklogBoard.jsx` foi atualizado para:

1.  **Polling Inteligente**:
    -   Se status == `running`: Consulta a cada **5 segundos**.
    -   Se status != `running`: Consulta a cada **30 segundos** (para detectar novas execuções iniciadas por outros usuários).
2.  **Persistência Visual**: O banner de "Última priorização" permanece visível mesmo após recarregar a página ou trocar de abas.

### Chat
O agente possui a ferramenta `check_prioritization_status` para responder perguntas como "A priorização já terminou?" consultando o DynamoDB.

## 🛠️ Detalhes Técnicos

### Backend (`app/core/agent.py`)
```python
# Exemplo simplificado
def prioritize_backlog():
    # Define status como running
    save_status("running")
    
    # Inicia thread
    thread = threading.Thread(target=execute_prioritization)
    thread.daemon = True
    thread.start()
    
    return "Priorização iniciada!"
```

### Frontend (`BacklogBoard.jsx`)
```javascript
useEffect(() => {
    // Lógica de polling adaptativo
    const interval = setInterval(() => {
        fetchStatus();
    }, status === 'running' ? 5000 : 30000);
    return () => clearInterval(interval);
}, [status]);
```
