const { useState, useEffect, useRef } = React;

function ChatInterface({ messages, setMessages, conversationId, setConversationId }) {
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        // Add empty assistant message to start streaming into
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch('chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    message: userMsg.content,
                    conversation_id: conversationId
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const newConvId = response.headers.get('X-Conversation-ID');
            if (newConvId) {
                setConversationId(newConvId);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    break;
                }

                const chunk = decoder.decode(value, { stream: true });

                setMessages(prev => {
                    const newMessages = [...prev];
                    const lastMsg = newMessages[newMessages.length - 1];
                    if (lastMsg.role === 'assistant') {
                        lastMsg.content += chunk;
                    }
                    return newMessages;
                });
            }

        } catch (error) {
            console.error("Erro no chat:", error);
            setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg.role === 'assistant') {
                    lastMsg.content += "\n\n[Erro: Não foi possível processar a resposta.]";
                }
                return newMessages;
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-white">
            <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scroll" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="text-center text-gray-400 mt-10">
                        <p>Olá! Sou seu assistente de backlog.</p>
                        <p className="text-sm">Peça para eu adicionar itens ou priorizar seu backlog.</p>
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-indigo-100 text-indigo-900' : 'bg-gray-100 text-gray-800'}`}>
                            <p className="whitespace-pre-wrap">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-100 p-3 rounded-lg">
                            <span className="animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}
            </div>
            <div className="p-4 border-t bg-gray-50 shrink-0">
                <div className="flex gap-2 items-end">
                    <textarea
                        className="flex-1 border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                        placeholder="Digite sua mensagem... (Ctrl+Enter para enviar)"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && e.ctrlKey) {
                                e.preventDefault();
                                sendMessage();
                            }
                        }}
                        disabled={loading}
                        rows={4}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading}
                        className="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 disabled:opacity-50 h-fit"
                    >
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
}
