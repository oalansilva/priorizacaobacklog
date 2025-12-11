function RoadmapHistory() {
    const [roadmaps, setRoadmaps] = React.useState([]);
    const [loading, setLoading] = React.useState(true);
    const [selectedRoadmap, setSelectedRoadmap] = React.useState(null);

    React.useEffect(() => {
        fetchRoadmaps();
    }, []);

    const fetchRoadmaps = async () => {
        try {
            setLoading(true);
            const response = await axios.get('roadmaps/');
            setRoadmaps(response.data);
        } catch (error) {
            console.error('Erro ao carregar roadmaps:', error);
        } finally {
            setLoading(false);
        }
    };

    const exportRoadmap = (roadmapId) => {
        window.location.href = `roadmaps/${roadmapId}/export`;
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

    if (selectedRoadmap) {
        const priorizados = selectedRoadmap.itens.filter(i => i.status === 'Priorizado').sort((a, b) => a.prioridade - b.prioridade);
        const despriorizados = selectedRoadmap.itens.filter(i => i.status === 'Despriorizado').sort((a, b) => a.prioridade - b.prioridade);

        return (
            <div className="p-6">
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
                    <h3 className="text-lg font-semibold mb-4">Resumo</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <p className="text-sm text-gray-600">Data</p>
                            <p className="font-semibold">{formatDate(selectedRoadmap.created_at)}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Capacidade Total</p>
                            <p className="font-semibold">{selectedRoadmap.capacidade_total}h</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Itens Priorizados</p>
                            <p className="font-semibold text-green-600">{selectedRoadmap.itens_priorizados}</p>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600">Horas Alocadas</p>
                            <p className="font-semibold">{selectedRoadmap.horas_alocadas}h</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Priorizados */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold mb-4 text-green-700">
                            ✅ Priorizados ({priorizados.length})
                        </h3>
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {priorizados.map((item) => (
                                <div key={item.id} className="border-l-4 border-green-500 bg-green-50 p-3 rounded">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <span className="inline-block bg-green-600 text-white text-xs px-2 py-1 rounded mr-2">
                                                #{item.prioridade}
                                            </span>
                                            <span className="font-semibold">{item.titulo}</span>
                                        </div>
                                        <span className="text-sm text-gray-600">{item.esforco_estimado}h</span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">{item.area}</p>
                                    <p className="text-sm text-gray-500 mt-1">Score: {item.score.toFixed(1)}%</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Despriorizados */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold mb-4 text-red-700">
                            ❌ Despriorizados ({despriorizados.length})
                        </h3>
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                            {despriorizados.map((item) => (
                                <div key={item.id} className="border-l-4 border-red-500 bg-red-50 p-3 rounded">
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <span className="inline-block bg-red-600 text-white text-xs px-2 py-1 rounded mr-2">
                                                #{item.prioridade}
                                            </span>
                                            <span className="font-semibold">{item.titulo}</span>
                                        </div>
                                        <span className="text-sm text-gray-600">{item.esforco_estimado}h</span>
                                    </div>
                                    <p className="text-sm text-gray-600 mt-1">{item.area}</p>
                                    <p className="text-sm text-gray-500 mt-1">Score: {item.score.toFixed(1)}%</p>
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
