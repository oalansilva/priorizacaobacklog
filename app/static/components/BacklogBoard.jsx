const { useState, useEffect } = React;

function BacklogBoard() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingItem, setEditingItem] = useState(null);

    const fetchItems = async () => {
        try {
            const response = await axios.get('/items/');
            setItems(response.data);
        } catch (error) {
            console.error("Erro ao buscar itens:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdateItem = async (updatedItem) => {
        try {
            await axios.put(`/items/${updatedItem.id}`, updatedItem);
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
            await axios.delete(`/items/${itemId}`);
            fetchItems();
        } catch (error) {
            console.error("Erro ao deletar item:", error);
            alert("Erro ao deletar item. Verifique o console.");
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    if (loading) return <div className="p-10 text-center">Carregando backlog...</div>;

    return (
        <div className="h-full overflow-y-auto p-6 bg-gray-50 relative">
            {editingItem && (
                <EditItemModal
                    item={editingItem}
                    onClose={() => setEditingItem(null)}
                    onSave={handleUpdateItem}
                />
            )}

            <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Backlog de Demandas</h2>
                <button onClick={fetchItems} className="text-indigo-600 hover:text-indigo-800 text-sm">Atualizar</button>
            </div>

            {items.length === 0 ? (
                <div className="text-center text-gray-500 py-10 border-2 border-dashed rounded-lg">
                    O backlog está vazio. Use o chat para adicionar itens.
                </div>
            ) : (
                <div className="grid gap-4">
                    {items.map(item => (
                        <div key={item.id} className="bg-white p-4 rounded-lg shadow border-l-4 border-indigo-500 hover:shadow-md transition-shadow group">
                            <div className="flex justify-between items-start">
                                <div className="flex-1">
                                    <div className="flex justify-between items-start">
                                        <h3 className="font-bold text-lg text-gray-900">{item.titulo}</h3>
                                        <div className="flex items-center gap-2">
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${item.status === 'Priorizado' ? 'bg-green-100 text-green-800' :
                                                item.status === 'Despriorizado' ? 'bg-red-100 text-red-800' :
                                                    'bg-blue-100 text-blue-800'
                                                }`}>
                                                {item.status}
                                            </span>
                                            <button
                                                onClick={() => setEditingItem(item)}
                                                className="text-gray-400 hover:text-indigo-600 p-1 rounded hover:bg-indigo-50 transition-colors"
                                                title="Editar Item"
                                            >
                                                ✎
                                            </button>
                                            <button
                                                onClick={() => handleDeleteItem(item.id, item.titulo)}
                                                className="text-gray-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-colors"
                                                title="Deletar Item"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                    <p className="text-gray-600 mt-1">{item.descricao}</p>
                                    {item.justificativa && (
                                        <div className="mt-2 p-2 bg-gray-50 border border-gray-200 rounded text-sm text-gray-700 italic">
                                            <span className="font-semibold not-italic">Justificativa:</span> {item.justificativa}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="mt-4 flex gap-4 text-sm text-gray-500">
                                <span className="flex items-center gap-1">
                                    ⏱️ Esforço: <span className="font-medium text-gray-700">{item.esforco_estimado}h</span>
                                </span>
                                <span className="flex items-center gap-1">
                                    📁 Área: <span className="font-medium text-gray-700">{item.area}</span>
                                </span>
                                {item.categoria && (
                                    <span className="flex items-center gap-1">
                                        🏷️ Categoria: <span className="font-medium text-gray-700">{item.categoria}</span>
                                    </span>
                                )}
                            </div>
                            <div className="mt-3 flex flex-wrap gap-2">
                                {item.impacto_financeiro === 'Sim' && (
                                    <span className="px-2 py-1 bg-green-50 text-green-700 rounded text-xs">💰 Impacto Financeiro</span>
                                )}
                                {item.impacto_negocios === 'Sim' && (
                                    <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">📈 Impacto Negócios</span>
                                )}
                                {item.impacto_cliente === 'Sim' && (
                                    <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs">👥 Impacto Cliente</span>
                                )}
                                {item.okr === 'Sim' && (
                                    <span className="px-2 py-1 bg-yellow-50 text-yellow-700 rounded text-xs">🎯 OKR</span>
                                )}
                                {item.estimado_qp === 'Sim' && (
                                    <span className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded text-xs">📋 Estimado QP</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
