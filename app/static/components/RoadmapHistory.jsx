function RoadmapHistory() {
    const [roadmaps, setRoadmaps] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [selectedRoadmap, setSelectedRoadmap] = React.useState(null);
    const [viewingJustification, setViewingJustification] = React.useState(null);

    React.useEffect(() => {
        fetchRoadmaps();
    }, []);

    const fetchRoadmaps = async () => {
        try {
            setLoading(true);
            const response = await axios.get('roadmaps');
            setRoadmaps(response.data);
        } catch (error) {
            console.error('Erro ao carregar roadmaps:', error);
        } finally {
            setLoading(false);
        }
    };

    const exportRoadmap = async (roadmapId) => {
        try {
            console.log('Exportando CSV para roadmap:', roadmapId);
            console.log('Token de autenticação:', axios.defaults.headers.common['Authorization'] ? 'Presente' : 'AUSENTE');

            const response = await axios.get(`roadmaps/${roadmapId}/export`, {
                responseType: 'blob'
            });

            console.log('CSV recebido com sucesso, tamanho:', response.data.size);

            const url = window.URL.createObjectURL(response.data);
            const link = document.createElement('a');
            link.href = url;

            // Extract filename from header if possible, default to timestamped name
            let filename = `roadmap_${new Date().toISOString().slice(0, 10)}.csv`;
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

            console.log('Download do CSV iniciado:', filename);
        } catch (error) {
            console.error('Erro ao exportar CSV:', error);
            console.error('Detalhes do erro:', error.response?.data, error.response?.status);

            // Tentar ler a mensagem de erro do blob (se possível)
            if (error.response && error.response.data instanceof Blob) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorObj = JSON.parse(reader.result);
                        alert(`Erro ao baixar CSV: ${errorObj.detail || 'Erro desconhecido'}`);
                    } catch (e) {
                        alert('Erro ao exportar CSV. Verifique se você está autenticado.');
                    }
                };
                reader.readAsText(error.response.data);
            } else {
                const errorMsg = error.response?.data?.detail || error.message || 'Erro desconhecido';
                alert(`Erro ao exportar CSV: ${errorMsg}`);
            }
        }
    };

    const exportPdf = async (roadmapId) => {
        try {
            // Feedback visual de carregamento
            const originalText = document.activeElement ? document.activeElement.innerText : '';
            if (document.activeElement && document.activeElement.tagName === 'BUTTON') {
                document.activeElement.innerText = '⏳ Baixando...';
                document.activeElement.disabled = true;
            }

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

            // Extract filename from header if possible, default to timestamped name
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

            // Tentar ler a mensagem de erro do blob (se possível)
            if (error.response && error.response.data instanceof Blob) {
                const reader = new FileReader();
                reader.onload = () => {
                    try {
                        const errorObj = JSON.parse(reader.result);
                        alert(`Erro ao baixar PDF: ${errorObj.detail || 'Erro desconhecido'}`);
                    } catch (e) {
                        alert('Ocorreu um erro ao gerar o PDF. Tente novamente.');
                    }
                };
                reader.readAsText(error.response.data);
            } else {
                alert('Erro ao conectar com o servidor para gerar o PDF.');
            }
        } finally {
            // Restaurar botão (aproximado, pois o foco pode ter mudado, mas ajuda na UX básica)
            if (document.activeElement && document.activeElement.tagName === 'BUTTON') {
                document.activeElement.innerText = '📄 PDF'; // Reset genérico ou tentar restaurar
                document.activeElement.disabled = false;
            }
            // Recarregar a lista para casos de restauração de estado UI geral
            // fetchRoadmaps(); 
        }
    };

    const deleteRoadmap = async (roadmapId) => {
        if (!confirm('Tem certeza que deseja deletar este roadmap?')) {
            return;
        }

        try {
            await axios.delete(`roadmaps/${roadmapId}`);
            fetchRoadmaps(); // Recarregar lista
        } catch (error) {
            console.error('Erro ao deletar roadmap:', error);
            alert('Erro ao deletar roadmap');
        }
    };

    const viewDetails = (roadmap) => {
        setSelectedRoadmap(roadmap);
    };

    const closeDetails = () => {
        setSelectedRoadmap(null);
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

    if (loading) {
        return (
            <div className="p-6">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                    <p className="mt-2 text-gray-600">Carregando roadmaps...</p>
                </div>
            </div>
        );
    }

    // Modal de Justificativa
    const JustificationModal = () => {
        if (!viewingJustification) return null;

        return (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4">
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
                        <h4 className="font-semibold text-gray-700 mb-2">Justificativa Histórica:</h4>
                        <div className="bg-gray-50 p-3 rounded border border-gray-100">
                            <p className="text-gray-600 whitespace-pre-wrap">
                                {viewingJustification.justificativa || 'Nenhuma justificativa registrada para este item neste roadmap.'}
                            </p>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">
                            * Esta justificativa reflete o momento em que o roadmap foi gerado.
                        </p>
                    </div>
                </div>
            </div>
        );
    };

    if (selectedRoadmap) {
        const priorizados = selectedRoadmap.itens.filter(i => i.status === 'Priorizado').sort((a, b) => a.prioridade - b.prioridade);
        const despriorizados = selectedRoadmap.itens.filter(i => i.status === 'Despriorizado').sort((a, b) => a.prioridade - b.prioridade);

        return (
            <div className="p-6 relative">
                <JustificationModal />
                <div className="mb-4 flex justify-between items-center">
                    <h2 className="text-2xl font-bold">Detalhes do Roadmap</h2>
                    <button
                        onClick={closeDetails}
                        className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                        ← Voltar
                    </button>
                </div>

                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h3 className="text-lg font-semibold mb-4">Resumo da Capacidade</h3>
                    {(() => {
                        const upstreamHours = priorizados
                            .filter(i => i.workflow_stage === 'upstream')
                            .reduce((acc, curr) => acc + (curr.esforco_estimado || 0), 0);

                        const downstreamHours = priorizados
                            .filter(i => i.workflow_stage === 'downstream')
                            .reduce((acc, curr) => acc + (curr.esforco_estimado || 0), 0);

                        const sustentacaoHours = selectedRoadmap.capacidade_total - selectedRoadmap.capacidade_iniciativas;

                        const despriorizadosHours = despriorizados
                            .reduce((acc, curr) => acc + (curr.esforco_estimado || 0), 0);

                        return (
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <div className="bg-gray-50 p-3 rounded border border-gray-100">
                                    <p className="text-xs text-gray-500 uppercase font-bold">Data</p>
                                    <p className="font-semibold text-gray-900">{formatDate(selectedRoadmap.created_at)}</p>
                                    <p className="text-xs text-gray-400 mt-1">Total: {selectedRoadmap.capacidade_total}h</p>
                                </div>
                                <div className="bg-blue-50 p-3 rounded border border-blue-100">
                                    <p className="text-xs text-blue-600 uppercase font-bold">📋 Upstream</p>
                                    <p className="font-semibold text-blue-900">{upstreamHours}h</p>
                                    <p className="text-xs text-blue-500 mt-1">
                                        {((upstreamHours / selectedRoadmap.capacidade_total) * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div className="bg-green-50 p-3 rounded border border-green-100">
                                    <p className="text-xs text-green-600 uppercase font-bold">🔨 Downstream</p>
                                    <p className="font-semibold text-green-900">{downstreamHours}h</p>
                                    <p className="text-xs text-green-500 mt-1">
                                        {((downstreamHours / selectedRoadmap.capacidade_total) * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div className="bg-orange-50 p-3 rounded border border-orange-100">
                                    <p className="text-xs text-orange-600 uppercase font-bold">🔧 Sustentação</p>
                                    <p className="font-semibold text-orange-900">{Math.round(sustentacaoHours)}h</p>
                                    <p className="text-xs text-orange-500 mt-1">
                                        {((sustentacaoHours / selectedRoadmap.capacidade_total) * 100).toFixed(1)}% (Reserva)
                                    </p>
                                </div>
                                <div className="bg-red-50 p-3 rounded border border-red-100">
                                    <p className="text-xs text-red-600 uppercase font-bold">❌ Despriorizados</p>
                                    <p className="font-semibold text-red-900">{despriorizadosHours}h</p>
                                    <p className="text-xs text-red-500 mt-1">
                                        {despriorizados.length} itens excedentes
                                    </p>
                                </div>
                            </div>
                        );
                    })()}
                </div>

                {/* Group by Workflow Stage */}
                <div className="space-y-6">
                    {/* Upstream Items */}
                    {(() => {
                        const upstreamItems = priorizados.filter(i => i.workflow_stage === 'upstream');
                        if (upstreamItems.length === 0) return null;

                        return (
                            <div className="bg-white rounded-lg shadow-md border-l-4 border-blue-500">
                                <div className="bg-blue-50 px-6 py-4 border-b border-blue-100">
                                    <h3 className="text-lg font-semibold text-blue-900 flex items-center gap-2">
                                        📋 Upstream - Descoberta e Design
                                        <span className="text-sm font-normal text-blue-600">
                                            ({upstreamItems.length} {upstreamItems.length === 1 ? 'item' : 'itens'})
                                        </span>
                                    </h3>
                                    <p className="text-sm text-blue-700 mt-1">
                                        Pesquisa, validação, design e planejamento
                                    </p>
                                </div>
                                <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
                                    {upstreamItems.map((item) => (
                                        <div key={item.id} className="border-l-4 border-blue-400 bg-blue-50 p-4 rounded-r hover:bg-blue-100 transition-colors">
                                            <div className="flex justify-between items-start">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="inline-block bg-blue-600 text-white text-xs px-2 py-1 rounded font-bold">
                                                            #{item.prioridade}
                                                        </span>
                                                        <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-semibold">
                                                            ✅ Priorizado
                                                        </span>
                                                    </div>
                                                    <span className="font-semibold text-gray-900">{item.titulo}</span>
                                                </div>
                                                <div className="flex items-center gap-2 ml-4">
                                                    {item.justificativa && (
                                                        <button
                                                            onClick={() => setViewingJustification(item)}
                                                            className="text-gray-400 hover:text-blue-600 p-1 rounded hover:bg-blue-200 transition-colors"
                                                            title="Ver Justificativa"
                                                        >
                                                            💬
                                                        </button>
                                                    )}
                                                    <span className="text-sm font-semibold text-gray-700 bg-white px-2 py-1 rounded">
                                                        ⏱️ {item.esforco_estimado}h
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="mt-2 flex items-center gap-4 text-sm">
                                                <span className="text-gray-600">📁 {item.area}</span>
                                                <span className="text-gray-500">Score: {item.score.toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })()}

                    {/* Downstream Items */}
                    {(() => {
                        const downstreamItems = priorizados.filter(i => i.workflow_stage === 'downstream');
                        if (downstreamItems.length === 0) return null;

                        return (
                            <div className="bg-white rounded-lg shadow-md border-l-4 border-green-500">
                                <div className="bg-green-50 px-6 py-4 border-b border-green-100">
                                    <h3 className="text-lg font-semibold text-green-900 flex items-center gap-2">
                                        🔨 Downstream - Implementação
                                        <span className="text-sm font-normal text-green-600">
                                            ({downstreamItems.length} {downstreamItems.length === 1 ? 'item' : 'itens'})
                                        </span>
                                    </h3>
                                    <p className="text-sm text-green-700 mt-1">
                                        Desenvolvimento, integração e entrega
                                    </p>
                                </div>
                                <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
                                    {downstreamItems.map((item) => (
                                        <div key={item.id} className="border-l-4 border-green-400 bg-green-50 p-4 rounded-r hover:bg-green-100 transition-colors">
                                            <div className="flex justify-between items-start">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="inline-block bg-green-600 text-white text-xs px-2 py-1 rounded font-bold">
                                                            #{item.prioridade}
                                                        </span>
                                                        <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded font-semibold">
                                                            ✅ Priorizado
                                                        </span>
                                                    </div>
                                                    <span className="font-semibold text-gray-900">{item.titulo}</span>
                                                </div>
                                                <div className="flex items-center gap-2 ml-4">
                                                    {item.justificativa && (
                                                        <button
                                                            onClick={() => setViewingJustification(item)}
                                                            className="text-gray-400 hover:text-green-600 p-1 rounded hover:bg-green-200 transition-colors"
                                                            title="Ver Justificativa"
                                                        >
                                                            💬
                                                        </button>
                                                    )}
                                                    <span className="text-sm font-semibold text-gray-700 bg-white px-2 py-1 rounded">
                                                        ⏱️ {item.esforco_estimado}h
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="mt-2 flex items-center gap-4 text-sm">
                                                <span className="text-gray-600">📁 {item.area}</span>
                                                <span className="text-gray-500">Score: {item.score.toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })()}

                    {/* Despriorizados */}
                    <div className="bg-white rounded-lg shadow-md border-l-4 border-red-500">
                        <div className="bg-red-50 px-6 py-4 border-b border-red-100">
                            <h3 className="text-lg font-semibold text-red-900 flex items-center gap-2">
                                ❌ Despriorizados
                                <span className="text-sm font-normal text-red-600">
                                    ({despriorizados.length} {despriorizados.length === 1 ? 'item' : 'itens'})
                                </span>
                            </h3>
                            <p className="text-sm text-red-700 mt-1">
                                Itens que não cabem na capacidade do trimestre
                            </p>
                        </div>
                        <div className="p-6 space-y-3 max-h-96 overflow-y-auto">
                            {despriorizados.map((item) => (
                                <div key={item.id} className="border-l-4 border-red-400 bg-red-50 p-4 rounded-r hover:bg-red-100 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-2">
                                                <span className="inline-block bg-red-600 text-white text-xs px-2 py-1 rounded font-bold">
                                                    #{item.prioridade}
                                                </span>
                                                {item.workflow_stage && (
                                                    <span className={`inline-block text-xs px-2 py-1 rounded font-semibold ${item.workflow_stage === 'upstream' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'
                                                        }`}>
                                                        {item.workflow_stage === 'upstream' ? '📋 Upstream' : '🔨 Downstream'}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="font-semibold text-gray-900">{item.titulo}</span>
                                        </div>
                                        <div className="flex items-center gap-2 ml-4">
                                            {item.justificativa && (
                                                <button
                                                    onClick={() => setViewingJustification(item)}
                                                    className="text-gray-400 hover:text-red-600 p-1 rounded hover:bg-red-200 transition-colors"
                                                    title="Ver Justificativa"
                                                >
                                                    💬
                                                </button>
                                            )}
                                            <span className="text-sm font-semibold text-gray-700 bg-white px-2 py-1 rounded">
                                                ⏱️ {item.esforco_estimado}h
                                            </span>
                                        </div>
                                    </div>
                                    <div className="mt-2 flex items-center gap-4 text-sm">
                                        <span className="text-gray-600">📁 {item.area}</span>
                                        <span className="text-gray-500">Score: {item.score.toFixed(1)}%</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6">
            <div className="mb-6">
                <h2 className="text-2xl font-bold mb-2">Histórico de Roadmaps</h2>
                <p className="text-gray-600">Visualize e exporte roadmaps de priorizações anteriores</p>
            </div>

            {roadmaps.length === 0 ? (
                <div className="bg-white rounded-lg shadow p-8 text-center">
                    <p className="text-gray-500">Nenhum roadmap encontrado.</p>
                    <p className="text-sm text-gray-400 mt-2">Execute uma priorização para gerar o primeiro roadmap.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {roadmaps.map((roadmap) => (
                        <div key={roadmap.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
                            <div className="p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-sm text-gray-500">
                                        📅 {formatDate(roadmap.created_at)}
                                    </span>
                                </div>

                                <div className="space-y-3 mb-4">
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-600">Total de Itens</span>
                                        <span className="font-semibold">{roadmap.total_itens}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-600">Priorizados</span>
                                        <span className="font-semibold text-green-600">{roadmap.itens_priorizados}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-600">Despriorizados</span>
                                        <span className="font-semibold text-red-600">{roadmap.itens_despriorizados}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-sm text-gray-600">Horas Alocadas</span>
                                        <span className="font-semibold">{roadmap.horas_alocadas}h</span>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <button
                                        onClick={() => viewDetails(roadmap)}
                                        className="flex-1 px-3 py-2 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
                                    >
                                        👁️ Ver
                                    </button>
                                    <button
                                        onClick={() => exportRoadmap(roadmap.id)}
                                        className="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700"
                                    >
                                        📥 CSV
                                    </button>
                                    <button
                                        onClick={() => exportPdf(roadmap.id)}
                                        className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                    >
                                        📄 PDF
                                    </button>
                                    <button
                                        onClick={() => deleteRoadmap(roadmap.id)}
                                        className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700"
                                    >
                                        🗑️
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
