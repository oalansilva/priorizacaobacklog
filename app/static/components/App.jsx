const { useState } = React;

function App() {
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([]);
    const [conversationId, setConversationId] = useState(null);

    return (
        <div className="flex flex-col h-full max-w-5xl mx-auto w-full bg-white shadow-xl overflow-hidden">
            <header className="bg-indigo-600 text-white p-3 sm:p-4 flex justify-between items-center shrink-0">
                <h1 className="text-lg sm:text-xl font-bold flex items-center gap-2">
                    🤖 <span className="hidden sm:inline">Gênio Priorizador</span><span className="sm:hidden">Priorizador</span>
                </h1>
                <nav className="flex gap-2 sm:gap-4">
                    <button
                        onClick={() => setActiveTab('chat')}
                        className={`px-2 sm:px-3 py-1 rounded text-sm sm:text-base ${activeTab === 'chat' ? 'bg-indigo-800' : 'hover:bg-indigo-700'}`}
                    >
                        Chat
                    </button>
                    <button
                        onClick={() => setActiveTab('backlog')}
                        className={`px-2 sm:px-3 py-1 rounded text-sm sm:text-base ${activeTab === 'backlog' ? 'bg-indigo-800' : 'hover:bg-indigo-700'}`}
                    >
                        Backlog
                    </button>
                    <button
                        onClick={() => setActiveTab('setup')}
                        className={`px-2 sm:px-3 py-1 rounded text-sm sm:text-base ${activeTab === 'setup' ? 'bg-indigo-800' : 'hover:bg-indigo-700'}`}
                    >
                        Setup
                    </button>
                </nav>
            </header>

            <main className="flex-1 overflow-hidden relative bg-gray-50">
                {activeTab === 'chat' && (
                    <ChatInterface
                        messages={messages}
                        setMessages={setMessages}
                        conversationId={conversationId}
                        setConversationId={setConversationId}
                    />
                )}
                {activeTab === 'backlog' && <BacklogBoard />}
                {activeTab === 'setup' && <SetupPanel />}
            </main>
        </div>
    );
}
