const { useState } = React;

function EditItemModal({ item, onClose, onSave }) {
    const [formData, setFormData] = useState({ ...item });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div className="p-6 border-b flex justify-between items-center">
                    <h3 className="text-xl font-bold text-gray-800">Editar Item</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
                </div>
                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700">Título</label>
                            <input type="text" name="titulo" value={formData.titulo} onChange={handleChange} className="mt-1 w-full border rounded p-2" required />
                        </div>
                        <div className="col-span-2">
                            <label className="block text-sm font-medium text-gray-700">Descrição</label>
                            <textarea name="descricao" value={formData.descricao} onChange={handleChange} className="mt-1 w-full border rounded p-2" rows="3" required />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Esforço (horas)</label>
                            <input type="number" name="esforco_estimado" value={formData.esforco_estimado} onChange={handleChange} className="mt-1 w-full border rounded p-2" required />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Área</label>
                            <input type="text" name="area" value={formData.area} onChange={handleChange} className="mt-1 w-full border rounded p-2" required />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Categoria</label>
                            <input type="text" name="categoria" value={formData.categoria || ''} onChange={handleChange} className="mt-1 w-full border rounded p-2" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Status</label>
                            <select name="status" value={formData.status} onChange={handleChange} className="mt-1 w-full border rounded p-2">
                                <option value="Novo">Novo</option>
                                <option value="Priorizado">Priorizado</option>
                                <option value="Despriorizado">Despriorizado</option>
                            </select>
                        </div>
                    </div>

                    <div className="border-t pt-4">
                        <h4 className="font-medium text-gray-900 mb-3">Impactos e Classificações (Sim/Não)</h4>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                            {['impacto_financeiro', 'impacto_negocios', 'impacto_cliente', 'okr', 'must_have', 'estimado_qp'].map(field => (
                                <div key={field}>
                                    <label className="block text-xs font-medium text-gray-500 uppercase mb-1">{field.replace('_', ' ')}</label>
                                    <select name={field} value={formData[field]} onChange={handleChange} className="w-full border rounded p-2 text-sm">
                                        <option value="Sim">Sim</option>
                                        <option value="Não">Não</option>
                                    </select>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t mt-6">
                        <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 rounded hover:bg-gray-200">Cancelar</button>
                        <button type="submit" className="px-4 py-2 text-white bg-indigo-600 rounded hover:bg-indigo-700">Salvar Alterações</button>
                    </div>
                </form>
            </div>
        </div>
    );
}
