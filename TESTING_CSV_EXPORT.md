# Como Testar o CSV Export Corretamente

## ⚠️ IMPORTANTE: Não teste colando a URL diretamente no navegador!

Quando você cola a URL diretamente no navegador (como `https://...lambda-url.../roadmaps/.../export`), o navegador **NÃO envia o token de autenticação**, por isso você recebe o erro `{"detail":"Not authenticated"}`.

## ✅ Forma Correta de Testar

1. **Acesse a aplicação normalmente** através da URL base:
   ```
   https://4tgupu7jynssz7q4ivevmdmsau0hyxjd.lambda-url.us-east-1.on.aws/
   ```

2. **Faça login** com suas credenciais

3. **Navegue até a aba "Roadmaps"**

4. **Clique no botão "📥 CSV"** de um roadmap

5. **Abra o Console do Navegador** (F12) e verifique os logs:
   - Deve aparecer: `Token de autenticação: Presente`
   - Se aparecer `AUSENTE`, significa que o token não foi configurado corretamente

## 🔍 Debug Logs Adicionados

A nova versão inclui logs detalhados no console:

```javascript
// Antes da requisição
Exportando CSV para roadmap: <id>
Token de autenticação: Presente/AUSENTE

// Após sucesso
CSV recebido com sucesso, tamanho: <bytes>
Download do CSV iniciado: <filename>

// Em caso de erro
Erro ao exportar CSV: <detalhes>
Detalhes do erro: <response data> <status code>
```

## 🐛 Possíveis Problemas

### Problema 1: Cache do Navegador
**Sintoma**: Código antigo ainda está sendo executado  
**Solução**: 
- Pressione `Ctrl + Shift + R` (hard refresh)
- Ou limpe o cache do navegador
- Ou abra em aba anônima

### Problema 2: Token Ausente
**Sintoma**: Log mostra "Token de autenticação: AUSENTE"  
**Solução**:
- Faça logout e login novamente
- Verifique se o localStorage tem o token: `localStorage.getItem('access_token')`

### Problema 3: URL Direta
**Sintoma**: Erro 401 ao acessar URL diretamente  
**Solução**: 
- **NÃO acesse a URL de export diretamente**
- Use o botão dentro da aplicação

## 📝 Próximos Passos

Após testar corretamente através da aplicação:
1. Abra o console do navegador (F12)
2. Clique no botão "📥 CSV"
3. Copie todos os logs que aparecerem
4. Se houver erro, compartilhe os logs completos
