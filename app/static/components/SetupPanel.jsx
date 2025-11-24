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
                const response = await axios.get('/settings/');
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
            await axios.put('/settings/', settings);
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

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Reserva para Sustentação (%)</label>
                        <input
                            type="number"
                            name="percentual_sustentacao"
                            value={settings.percentual_sustentacao}
                            onChange={handleSettingChange}
                            className="w-full border rounded-lg p-3 text-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                        />
                        <p className="text-sm text-gray-500 mt-1">Percentual da capacidade reservado para bugs e manutenção.</p>
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
