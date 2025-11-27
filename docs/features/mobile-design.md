# Design Responsivo (Mobile First)

## 🎯 Objetivo

Garantir que a aplicação seja totalmente funcional e visualmente agradável em dispositivos móveis, permitindo que os usuários gerenciem o backlog de qualquer lugar.

## 📱 Princípios de Design

Adotamos uma abordagem **Mobile First**, priorizando a experiência em telas pequenas e expandindo para desktops.

### Principais Adaptações

#### 1. Header Responsivo
-   **Desktop**: Exibe "🤖 Gênio Priorizador" e botões com padding generoso.
-   **Mobile**: Simplifica para "🤖 Priorizador" e reduz o tamanho dos botões para caber na largura da tela.

#### 2. Backlog Board
-   **Grid de Estatísticas**:
    -   Desktop: Espaçamento amplo (`gap-2`, `p-2`).
    -   Mobile: Compacto (`gap-1.5`, `p-1.5`), fontes reduzidas para exibir números sem quebrar o layout.
-   **Cards de Itens**:
    -   Layout flexível que se adapta à largura.
    -   Uso de `break-words` para evitar que títulos longos cortem ou gerem scroll horizontal.
    -   Tags e botões de ação redimensionados para toque.

#### 3. Prevenção de Scroll Horizontal
-   Aplicação de `overflow-x: hidden` no `body`.
-   Configuração correta da meta tag `viewport` em `index.html`.

## 🛠️ Implementação Técnica

Utilizamos as classes utilitárias do **Tailwind CSS** com prefixos responsivos:

-   `text-sm sm:text-base`: Fonte pequena no mobile, normal no desktop.
-   `p-2 sm:p-4`: Padding reduzido no mobile.
-   `hidden sm:inline`: Elementos que só aparecem em telas maiores.

### Exemplo de Código (`App.jsx`)

```jsx
<h1 className="text-lg sm:text-xl font-bold">
    🤖 <span className="hidden sm:inline">Gênio Priorizador</span>
       <span className="sm:hidden">Priorizador</span>
</h1>
```

## 🧪 Como Testar

1.  Abra a aplicação no navegador do celular.
2.  Ou use o **DevTools** do navegador (F12) -> Ícone de dispositivo móvel (Ctrl+Shift+M).
3.  Verifique se:
    -   Não há scroll horizontal indesejado.
    -   Todos os textos estão legíveis.
    -   Botões são clicáveis.
    -   O layout não quebra ao girar a tela.
