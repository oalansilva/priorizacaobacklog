const { useState, useEffect } = React;

function SetupPanel() {
    const [settings, setSettings] = useState({
        capacidade_total: 1000,
        percentual_sustentacao: 20,
        peso_financeiro: 25,
        peso_negocios: 25,
        peso_cliente: 25,
        peso_okr: 25
    });
    const [loading, setLoading] = useState(true);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const response = await axios.get('settings');
                if (response.data) setSettings(response.data);
            } catch (error) {
                console.error("Erro ao carregar configurações:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchSettings();
    }, []);

    const handleSettingChange = (e) => {
        const { name, value } = e.target;
        setSettings(prev => ({ ...prev, [name]: parseInt(value) || 0 }));
        setSaved(false);
    };

    const saveSettings = async () => {
        try {
            await axios.put('settings', settings);
            setSaved(true);
            setTimeout(() => setSaved(false), 3000);
        } catch (error) {
            console.error("Erro ao salvar configurações:", error);
            alert("Erro ao salvar configurações.");
        }
    };

    const totalWeights = (settings.peso_financeiro || 0) +
        (settings.peso_negocios || 0) +
        (settings.peso_cliente || 0) +
        (settings.peso_okr || 0);

    if (loading) return <div className="p-10 text-center">Carregando configurações...</div>;

    return (
        <div className="h-full overflow-y-auto p-6">
            <div className="max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-gray-800 mb-6">Configurações Globais</h2>

                <div className="bg-white p-8 rounded-lg shadow border border-gray-200 space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Capacidade Total do Trimestre (horas)</label>
                        <input
                            type="number"
                            name="capacidade_total"
                            value={settings.capacidade_total}
                            onChange={handleSettingChange}
                            className="w-full border rounded-lg p-3 text-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                        <p className="text-sm text-gray-500 mt-1">Total de horas disponíveis para desenvolvimento no período.</p>
                    </div>

                    <div className="border-t pt-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            Alocação de Capacidade por Workflow Stage
                            <span className={`ml-2 text-sm ${Math.abs(((settings.capacity_upstream_percent || 0) +
                                (settings.capacity_downstream_percent || 0) +
                                (settings.capacity_sustentacao_percent || 0)) - 100) < 0.01
                                ? 'text-green-600' : 'text-red-500'
                                }`}>
                                (Soma: {((settings.capacity_upstream_percent || 0) +
                                    (settings.capacity_downstream_percent || 0) +
                                    (settings.capacity_sustentacao_percent || 0)).toFixed(1)}%)
                            </span>
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-blue-700 mb-1 flex items-center gap-1">
                                    📋 Upstream (%)
                                </label>
                                <input
                                    type="number"
                                    name="capacity_upstream_percent"
                                    value={settings.capacity_upstream_percent || 40}
                                    onChange={(e) => {
                                        const value = parseFloat(e.target.value) || 0;
                                        setSettings(prev => ({ ...prev, capacity_upstream_percent: value }));
                                        setSaved(false);
                                    }}
                                    step="0.1"
                                    className="w-full border border-blue-200 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                                <p className="text-xs text-gray-500 mt-1">Descoberta, pesquisa, design</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-green-700 mb-1 flex items-center gap-1">
                                    🔨 Downstream (%)
                                </label>
                                <input
                                    type="number"
                                    name="capacity_downstream_percent"
                                    value={settings.capacity_downstream_percent || 40}
                                    onChange={(e) => {
                                        const value = parseFloat(e.target.value) || 0;
                                        setSettings(prev => ({ ...prev, capacity_downstream_percent: value }));
                                        setSaved(false);
                                    }}
                                    step="0.1"
                                    className="w-full border border-green-200 rounded-lg p-2 focus:ring-2 focus:ring-green-500 outline-none"
                                />
                                <p className="text-xs text-gray-500 mt-1">Implementação, entrega</p>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-orange-700 mb-1 flex items-center gap-1">
                                    🔧 Sustentação (%)
                                </label>
                                <input
                                    type="number"
                                    name="capacity_sustentacao_percent"
                                    value={settings.capacity_sustentacao_percent || 20}
                                    onChange={(e) => {
                                        const value = parseFloat(e.target.value) || 0;
                                        setSettings(prev => ({ ...prev, capacity_sustentacao_percent: value }));
                                        setSaved(false);
                                    }}
                                    step="0.1"
                                    className="w-full border border-orange-200 rounded-lg p-2 focus:ring-2 focus:ring-orange-500 outline-none"
                                />
                                <p className="text-xs text-gray-500 mt-1">Bugs, manutenção, suporte</p>
                            </div>
                        </div>
                        {Math.abs(((settings.capacity_upstream_percent || 0) +
                            (settings.capacity_downstream_percent || 0) +
                            (settings.capacity_sustentacao_percent || 0)) - 100) >= 0.01 && (
                                <p className="text-red-500 text-sm mt-2">⚠️ A soma dos percentuais deve ser exatamente 100%.</p>
                            )}
                    </div>

                    <div className="border-t pt-6">
                        <h3 className="text-lg font-medium text-gray-900 mb-4">
                            Pesos de Priorização
                            <span className={`ml-2 text-sm ${totalWeights === 100 ? 'text-green-600' : 'text-red-500'}`}>
                                (Soma: {totalWeights}%)
                            </span>
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {[
                                { key: 'peso_financeiro', label: 'Impacto Financeiro' },
                                { key: 'peso_negocios', label: 'Impacto Negócios' },
                                { key: 'peso_cliente', label: 'Impacto Cliente' },
                                { key: 'peso_okr', label: 'OKR' }
                            ].map(field => (
                                <div key={field.key}>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        {field.label} (%)
                                    </label>
                                    <input
                                        type="number"
                                        name={field.key}
                                        value={settings[field.key] || 0}
                                        onChange={handleSettingChange}
                                        className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-indigo-500 outline-none"
                                    />
                                </div>
                            ))}
                        </div>
                        {totalWeights !== 100 && (
                            <p className="text-red-500 text-sm mt-2">⚠️ A soma dos pesos deve ser exatamente 100% para uma priorização balanceada.</p>
                        )}
                    </div>

                    <div className="pt-6 border-t flex items-center gap-4">
                        <button
                            onClick={saveSettings}
                            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 font-medium transition-colors"
                        >
                            Salvar Configurações
                        </button>
                        {saved && <span className="text-green-600 font-medium animate-fade-in flex items-center gap-1">✅ Salvo com sucesso!</span>}
                    </div>
                </div>
            </div>
        </div>
    );
}
