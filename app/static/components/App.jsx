const { useState } = React;

function App() {
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([]);
    const [conversationId, setConversationId] = useState(null);

    const [version, setVersion] = useState('');

    React.useEffect(() => {
        fetch('version')
            .then(res => res.json())
            .then(data => setVersion(data.version))
            .catch(() => setVersion(''));
    }, []);

    return (
        <div className="flex flex-col h-full max-w-5xl mx-auto w-full bg-white shadow-xl overflow-hidden">
            <header className="bg-indigo-600 text-white p-3 sm:p-4 flex justify-between items-center shrink-0">
                <h1 className="text-lg sm:text-xl font-bold flex items-center gap-2">
                    🤖 <span className="hidden sm:inline">ARCADIA – Autonomous Roadmap & Decision AI</span><span className="sm:hidden">ARCADIA</span>
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

            <main className="flex-1 overflow-hidden relative bg-gray-50 flex flex-col">
                <div className="flex-1 overflow-auto">
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
                </div>

                {version && (
                    <footer className="bg-gray-100 text-gray-400 text-xs py-1 px-4 text-right border-t border-gray-200 shrink-0">
                        v{version}
                    </footer>
                )}
            </main>
        </div>
    );
}
