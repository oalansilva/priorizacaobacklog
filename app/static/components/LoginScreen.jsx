const { useState } = React;

function LoginScreen({ onLogin }) {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);

                const res = await axios.post('/auth/token', formData);
                onLogin(res.data.access_token);
            } else {
                await axios.post('/auth/register', {
                    email,
                    password,
                    full_name: fullName
                });

                // Auto login after register
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);
                const res = await axios.post('/auth/token', formData);
                onLogin(res.data.access_token);
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || 'Erro ao processar solicitação. Verifique suas credenciais.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-indigo-700 mb-2">ARCADIA</h1>
                    <p className="text-gray-500">Autonomous Roadmap & Decision AI</p>
                </div>

                <h2 className="text-xl font-semibold mb-6">
                    {isLogin ? 'Entrar em sua conta' : 'Criar nova conta'}
                </h2>

                {error && (
                    <div className="bg-red-50 text-red-700 p-3 rounded mb-4 text-sm">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Nome Completo</label>
                            <input
                                type="text"
                                required
                                className="w-full border rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                                value={fullName}
                                onChange={e => setFullName(e.target.value)}
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            required
                            className="w-full border rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Senha</label>
                        <input
                            type="password"
                            required
                            className="w-full border rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full bg-indigo-600 text-white py-2 px-4 rounded-md font-medium hover:bg-indigo-700 transition-colors ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
                    >
                        {loading ? 'Processando...' : (isLogin ? 'Entrar' : 'Criar Conta')}
                    </button>
                </form>

                <div className="mt-6 text-center text-sm">
                    <button
                        onClick={() => {
                            setIsLogin(!isLogin);
                            setError('');
                        }}
                        className="text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                        {isLogin ? 'Não tem uma conta? Crie agora' : 'Já tem conta? Entre aqui'}
                    </button>
                </div>
            </div>
        </div>
    );
}
