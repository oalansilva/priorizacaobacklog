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

        try {
            const response = await axios.post('/chat/', {
                message: userMsg.content,
                conversation_id: conversationId
            });

            const botMsg = { role: 'assistant', content: response.data.response };
            setMessages(prev => [...prev, botMsg]);
            setConversationId(response.data.conversation_id);
        } catch (error) {
            console.error("Erro no chat:", error);
            const errorMsg = error.response?.data?.detail || "Desculpe, ocorreu um erro ao processar sua mensagem.";
            setMessages(prev => [...prev, { role: 'assistant', content: errorMsg }]);
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
                <div className="flex gap-2">
                    <input
                        type="text"
                        className="flex-1 border rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="Digite sua mensagem..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        disabled={loading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading}
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                    >
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
}
