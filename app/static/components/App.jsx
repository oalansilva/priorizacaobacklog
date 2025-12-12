const { useState } = React;

function App() {
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([]);
    const [conversationId, setConversationId] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('access_token'));
    const [user, setUser] = useState(null); // Decode from token if needed

    const [version, setVersion] = useState('');

    React.useEffect(() => {
        fetch('version')
            .then(res => res.json())
            .then(data => setVersion(data.version))
            .catch(() => setVersion(''));
    }, []);

    const handleLogin = (newToken) => {
        localStorage.setItem('access_token', newToken);
        setToken(newToken);
        // Configure axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        setToken(null);
        setMessages([]);
        setConversationId(null);
        delete axios.defaults.headers.common['Authorization'];
    };

    // Initialize axios header if token exists on mount
    React.useEffect(() => {
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        }
    }, [token]);

    if (!token) {
        return <LoginScreen onLogin={handleLogin} />;
    }

    return (
        <div className="flex flex-col h-full max-w-5xl mx-auto w-full bg-white shadow-xl overflow-hidden">
            <header className="bg-indigo-600 text-white p-3 sm:p-4 flex justify-between items-center shrink-0">
                <h1 className="text-lg sm:text-xl font-bold flex items-center gap-2">
                    🤖 <span className="hidden sm:inline">ARCADIA – Autonomous Roadmap & Decision AI</span><span className="sm:hidden">ARCADIA</span>
                </h1>
                <div className="flex items-center gap-4">
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
                            onClick={() => setActiveTab('roadmaps')}
                            className={`px-2 sm:px-3 py-1 rounded text-sm sm:text-base ${activeTab === 'roadmaps' ? 'bg-indigo-800' : 'hover:bg-indigo-700'}`}
                        >
                            Roadmaps
                        </button>
                        <button
                            onClick={() => setActiveTab('setup')}
                            className={`px-2 sm:px-3 py-1 rounded text-sm sm:text-base ${activeTab === 'setup' ? 'bg-indigo-800' : 'hover:bg-indigo-700'}`}
                        >
                            Setup
                        </button>
                    </nav>
                    <button
                        onClick={handleLogout}
                        className="text-xs bg-indigo-700 hover:bg-indigo-800 px-2 py-1 rounded transition-colors"
                    >
                        Sair
                    </button>
                </div>
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
                    {activeTab === 'roadmaps' && <RoadmapHistory />}
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
