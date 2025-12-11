const { useState, useEffect } = React;

function BacklogBoard() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingItem, setEditingItem] = useState(null);
    const [viewingJustification, setViewingJustification] = useState(null);
    const [prioritizationStatus, setPrioritizationStatus] = useState(null);
    const [showRoadmaps, setShowRoadmaps] = useState(false);
    const [roadmaps, setRoadmaps] = useState([]);
    const [loadingRoadmaps, setLoadingRoadmaps] = useState(false);

    const fetchItems = async () => {
        try {
            const response = await axios.get('items/');
            setItems(response.data);
        } catch (error) {
            console.error("Erro ao buscar itens:", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchStatus = async () => {
        try {
            const response = await axios.get('items/prioritization-status');
            console.log("Status fetched:", response.data);
            console.log("Will display?", response.data.status !== 'none');
            setPrioritizationStatus(response.data);
        } catch (error) {
            console.error("Erro ao buscar status:", error);
        }
    };

    const handleUpdateItem = async (updatedItem) => {
        try {
            await axios.put(`items/${updatedItem.id}`, updatedItem);
            setEditingItem(null);
            fetchItems();
        } catch (error) {
            console.error("Erro ao atualizar item:", error);
            alert("Erro ao salvar alterações. Verifique o console.");
        }
    };

    const handleDeleteItem = async (itemId, itemTitle) => {
        if (!confirm(`Tem certeza que deseja deletar o item "${itemTitle}"?`)) {
            return;
        }

        try {
            await axios.delete(`items/${itemId}`);
            fetchItems();
        } catch (error) {
            console.error("Erro ao deletar item:", error);
            alert("Erro ao deletar item. Verifique o console.");
        }
    };

    const fetchRoadmaps = async () => {
        try {
            setLoadingRoadmaps(true);
            const response = await axios.get('roadmaps/');
            setRoadmaps(response.data);
            setShowRoadmaps(true);
        } catch (error) {
            console.error("Erro ao buscar roadmaps:", error);
            alert("Erro ao carregar roadmaps");
        } finally {
            setLoadingRoadmaps(false);
        }
    };

    const exportRoadmap = (roadmapId) => {
        window.location.href = `roadmaps/${roadmapId}/export`;
    };

    const exportPdf = async (roadmapId) => {
        try {
            const response = await axios.get(`roadmaps/${roadmapId}/export-pdf`, {
                responseType: 'blob',
                headers: {
                    'Accept': 'application/pdf'
                }
            });

            let blob = response.data;
            try {
                const text = await blob.text();
                if (text.startsWith('JVBERi')) {
                    console.log("Detectado PDF em Base64, decodificando...");
                    const binaryString = atob(text);
                    const bytes = new Uint8Array(binaryString.length);
                    for (let i = 0; i < binaryString.length; i++) {
                        bytes[i] = binaryString.charCodeAt(i);
                    }
                    blob = new Blob([bytes], { type: 'application/pdf' });
                }
            } catch (e) {
                console.log("Blob não é texto ou erro ao verificar Base64:", e);
            }

            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;

            // Extract filename
            let filename = `roadmap_${new Date().toISOString().slice(0, 10)}.pdf`;
            const contentDisposition = response.headers['content-disposition'];
            if (contentDisposition) {
                const fileNameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
                if (fileNameMatch && fileNameMatch.length === 2)
                    filename = fileNameMatch[1];
            }

            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Erro ao exportar PDF:', error);
            // Tentar ler a mensagem de erro do blob
            if (error.response && error.response.data instanceof Blob) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorObj = JSON.parse(reader.result);
                        alert(`Erro: ${errorObj.detail || 'Falha na exportação'}`);
                    } catch (e) {
                        alert('Erro ao gerar PDF. Verifique se o roadmap ainda existe.');
                    }
                };
                reader.readAsText(error.response.data);
            } else {
                alert('Erro ao solicitar PDF.');
            }
        }
    };

    const formatDate = (isoDate) => {
        const date = new Date(isoDate);
        return date.toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'America/Sao_Paulo'
        });
    };

    useEffect(() => {
        fetchItems();
        fetchStatus();

        // Auto-refresh status every 5 seconds if prioritization is running
        const interval = setInterval(() => {
            if (prioritizationStatus?.status === 'running') {
                fetchStatus();
                fetchItems(); // Also refresh items to show updated results
            }
        }, 5000);

        return () => clearInterval(interval);
    }, [prioritizationStatus?.status]);

    // Calculate statistics
    const stats = {
        priorizados: {
            count: items.filter(i => i.status === 'Priorizado').length,
            hours: items.filter(i => i.status === 'Priorizado').reduce((sum, i) => sum + (i.esforco_estimado || 0), 0)
        },
        despriorizados: {
            count: items.filter(i => i.status === 'Despriorizado').length,
            hours: items.filter(i => i.status === 'Despriorizado').reduce((sum, i) => sum + (i.esforco_estimado || 0), 0)
        },
        novos: {
            count: items.filter(i => i.status === 'Novo').length,
            hours: items.filter(i => i.status === 'Novo').reduce((sum, i) => sum + (i.esforco_estimado || 0), 0)
        }
    };

    if (loading) return <div className="p-10 text-center">Carregando backlog...</div>;

    // Sort items by priority (ascending)
    const sortedItems = [...items].sort((a, b) => (a.prioridade || 999) - (b.prioridade || 999));

    return (
        <div className="h-full overflow-y-auto p-4 bg-gray-50 relative">
            {editingItem && (
                <EditItemModal
                    item={editingItem}
                    onClose={() => setEditingItem(null)}
                    onSave={handleUpdateItem}
                />
            )}

            {viewingJustification && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                        <div className="p-4 border-b border-gray-200 flex justify-between items-start">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">{viewingJustification.titulo}</h3>
                                <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-semibold ${viewingJustification.status === 'Priorizado' ? 'bg-green-100 text-green-800' :
                                    viewingJustification.status === 'Despriorizado' ? 'bg-red-100 text-red-800' :
                                        'bg-blue-100 text-blue-800'
                                    }`}>
                                    {viewingJustification.status}
                                </span>
                            </div>
                            <button
                                onClick={() => setViewingJustification(null)}
                                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-4">
                            <h4 className="font-semibold text-gray-700 mb-2">Justificativa:</h4>
                            <p className="text-gray-600 whitespace-pre-wrap">
                                {viewingJustification.justificativa || 'Nenhuma justificativa disponível.'}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Roadmaps Modal */}
            {showRoadmaps && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
                        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
                            <h3 className="text-lg font-bold text-gray-900">📊 Histórico de Roadmaps</h3>
                            <button
                                onClick={() => setShowRoadmaps(false)}
                                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                            >
                                ×
                            </button>
                        </div>
                        <div className="p-4 overflow-y-auto flex-1">
                            {roadmaps.length === 0 ? (
                                <div className="text-center text-gray-500 py-8">
                                    Nenhum roadmap encontrado. Execute uma priorização para gerar o primeiro roadmap.
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    {roadmaps.map((roadmap) => (
                                        <div key={roadmap.id} className="bg-white border border-gray-200 rounded-lg shadow hover:shadow-md transition-shadow p-4">
                                            <div className="mb-3">
                                                <span className="text-sm text-gray-500">
                                                    📅 {formatDate(roadmap.created_at)}
                                                </span>
                                            </div>

                                            <div className="space-y-2 mb-4">
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-600">Total de Itens</span>
                                                    <span className="font-semibold">{roadmap.total_itens}</span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-600">Priorizados</span>
                                                    <span className="font-semibold text-green-600">{roadmap.itens_priorizados}</span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-600">Despriorizados</span>
                                                    <span className="font-semibold text-red-600">{roadmap.itens_despriorizados}</span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-gray-600">Horas Alocadas</span>
                                                    <span className="font-semibold">{roadmap.horas_alocadas}h</span>
                                                </div>
                                            </div>

                                            <div className="flex gap-2">
                                                <button
                                                    onClick={() => exportRoadmap(roadmap.id)}
                                                    className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                                                >
                                                    📥 CSV
                                                </button>
                                                <button
                                                    onClick={() => exportPdf(roadmap.id)}
                                                    className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                                                >
                                                    📄 PDF
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="sticky top-0 bg-gray-50 z-10 pb-2 sm:pb-3">
                <div className="flex justify-between items-center mb-2 sm:mb-3">
                    <h2 className="text-lg sm:text-xl font-bold text-gray-800">Backlog de Demandas</h2>
                    <div className="flex gap-2">
                        <button
                            onClick={fetchRoadmaps}
                            className="px-3 py-1.5 bg-indigo-600 text-white text-xs sm:text-sm font-medium rounded hover:bg-indigo-700 transition-colors"
                            disabled={loadingRoadmaps}
                        >
                            {loadingRoadmaps ? '...' : '📊 Roadmaps'}
                        </button>
                        <button
                            onClick={fetchItems}
                            className="text-indigo-600 hover:text-indigo-800 text-xs sm:text-sm font-medium"
                        >
                            Atualizar
                        </button>
                    </div>
                </div>

                {/* Summary Statistics */}
                <div className="grid grid-cols-3 gap-1.5 sm:gap-2 mb-2">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-1.5 sm:p-2">
                        <div className="text-xs font-medium text-green-700 mb-0.5">✅ Priorizados</div>
                        <div className="flex items-baseline gap-1 sm:gap-2">
                            <span className="text-base sm:text-lg font-bold text-green-900">{stats.priorizados.count}</span>
                            <span className="text-xs text-green-600">{stats.priorizados.hours}h</span>
                        </div>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-1.5 sm:p-2">
                        <div className="text-xs font-medium text-red-700 mb-0.5">❌ Despriorizados</div>
                        <div className="flex items-baseline gap-1 sm:gap-2">
                            <span className="text-base sm:text-lg font-bold text-red-900">{stats.despriorizados.count}</span>
                            <span className="text-xs text-red-600">{stats.despriorizados.hours}h</span>
                        </div>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-1.5 sm:p-2">
                        <div className="text-xs font-medium text-blue-700 mb-0.5">🆕 Novos</div>
                        <div className="flex items-baseline gap-1 sm:gap-2">
                            <span className="text-base sm:text-lg font-bold text-blue-900">{stats.novos.count}</span>
                            <span className="text-xs text-blue-600">{stats.novos.hours}h</span>
                        </div>
                    </div>
                </div>

                {/* Prioritization Status Indicator */}
                {prioritizationStatus && prioritizationStatus.status !== 'none' && (
                    <div className={`mb-2 p-2 rounded-lg border ${prioritizationStatus.status === 'running'
                        ? 'bg-yellow-50 border-yellow-200'
                        : prioritizationStatus.status === 'completed'
                            ? 'bg-green-50 border-green-200'
                            : 'bg-red-50 border-red-200'
                        }`}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                {prioritizationStatus.status === 'running' && (
                                    <>
                                        <div className="animate-spin h-4 w-4 border-2 border-yellow-600 border-t-transparent rounded-full"></div>
                                        <span className="text-sm font-medium text-yellow-800">
                                            Priorização em andamento...
                                        </span>
                                    </>
                                )}
                                {prioritizationStatus.status === 'completed' && (
                                    <>
                                        <span className="text-green-600">✅</span>
                                        <span className="text-sm font-medium text-green-800">
                                            Última priorização: {new Date(prioritizationStatus.timestamp).toLocaleString('pt-BR')}
                                        </span>
                                    </>
                                )}
                                {prioritizationStatus.status === 'error' && (
                                    <>
                                        <span className="text-red-600">❌</span>
                                        <span className="text-sm font-medium text-red-800">
                                            Erro na priorização
                                        </span>
                                    </>
                                )}
                            </div>
                            {prioritizationStatus.status === 'running' && (
                                <button
                                    onClick={fetchStatus}
                                    className="text-xs text-yellow-700 hover:text-yellow-900 font-medium"
                                >
                                    Atualizar
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {sortedItems.length === 0 ? (
                <div className="text-center text-gray-500 py-8 border-2 border-dashed rounded-lg">
                    O backlog está vazio. Use o chat para adicionar itens.
                </div>
            ) : (
                <div className="grid gap-2">
                    {sortedItems.map(item => (
                        <div key={item.id} className="bg-white p-2 sm:p-3 rounded-lg shadow-sm border-l-4 border-indigo-500 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start gap-2 sm:gap-3">
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-start gap-2 mb-1">
                                        <h3 className="font-bold text-sm sm:text-base text-gray-900 flex-1 break-words">
                                            {item.prioridade && item.prioridade < 999 ? (
                                                <span className="mr-2 inline-flex items-center justify-center w-5 h-5 sm:w-6 sm:h-6 bg-indigo-100 text-indigo-800 text-xs font-bold rounded-full">
                                                    #{item.prioridade}
                                                </span>
                                            ) : null}
                                            {item.titulo}
                                        </h3>
                                        <div className="flex items-center gap-1 sm:gap-1.5 flex-shrink-0">
                                            <span className={`px-1.5 sm:px-2 py-0.5 rounded text-xs font-semibold ${item.status === 'Priorizado' ? 'bg-green-100 text-green-800' :
                                                item.status === 'Despriorizado' ? 'bg-red-100 text-red-800' :
                                                    'bg-blue-100 text-blue-800'
                                                }`}>
                                                {item.status}
                                            </span>
                                            {item.justificativa && (
                                                <button
                                                    onClick={() => setViewingJustification(item)}
                                                    className="text-gray-400 hover:text-blue-600 p-0.5 sm:p-1 rounded hover:bg-blue-50 transition-colors text-sm"
                                                    title="Ver Justificativa"
                                                >
                                                    💬
                                                </button>
                                            )}
                                            <button
                                                onClick={() => setEditingItem(item)}
                                                className="text-gray-400 hover:text-indigo-600 p-0.5 sm:p-1 rounded hover:bg-indigo-50 transition-colors text-sm"
                                                title="Editar Item"
                                            >
                                                ✎
                                            </button>
                                            <button
                                                onClick={() => handleDeleteItem(item.id, item.titulo)}
                                                className="text-gray-400 hover:text-red-600 p-0.5 sm:p-1 rounded hover:bg-red-50 transition-colors text-sm"
                                                title="Deletar Item"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                    <p className="text-gray-600 text-xs sm:text-sm line-clamp-1 mb-2">{item.descricao}</p>

                                    <div className="flex flex-wrap gap-x-2 sm:gap-x-3 gap-y-1 text-xs text-gray-600 mb-2">
                                        <span className="flex items-center gap-1">
                                            ⏱️ <span className="font-medium text-gray-700">{item.esforco_estimado}h</span>
                                        </span>
                                        <span className="flex items-center gap-1">
                                            📁 <span className="font-medium text-gray-700">{item.area}</span>
                                        </span>
                                        {item.categoria && (
                                            <span className="flex items-center gap-1">
                                                🏷️ <span className="font-medium text-gray-700">{item.categoria}</span>
                                            </span>
                                        )}
                                    </div>

                                    <div className="flex flex-wrap gap-1 sm:gap-1.5">
                                        {item.impacto_financeiro === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs font-medium">💰 Financeiro</span>
                                        )}
                                        {item.impacto_negocios === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-medium">📈 Negócios</span>
                                        )}
                                        {item.impacto_cliente === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-purple-50 text-purple-700 rounded text-xs font-medium">👥 Cliente</span>
                                        )}
                                        {item.okr === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-yellow-50 text-yellow-700 rounded text-xs font-medium">🎯 OKR</span>
                                        )}
                                        {item.must_have === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-red-50 text-red-700 rounded text-xs font-medium border border-red-300">⚠️ Must Have</span>
                                        )}
                                        {item.estimado_qp === 'Sim' && (
                                            <span className="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs font-medium">📋 QP</span>
                                        )}
                                        {item.score !== undefined && item.score > 0 && (
                                            <span className="px-1.5 py-0.5 bg-yellow-100 text-yellow-800 rounded text-xs font-bold border border-yellow-300 flex items-center gap-1">
                                                ⭐ {item.score}%
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
