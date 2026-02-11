import React, { useState } from 'react';
import { X } from 'lucide-react';
import { createTextConsultation } from '../api/client';

interface TextNoteModalProps {
    onClose: () => void;
    onCreated: () => void;
}

const TextNoteModal: React.FC<TextNoteModalProps> = ({ onClose, onCreated }) => {
    const [text, setText] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!text.trim()) return;

        setSubmitting(true);
        try {
            await createTextConsultation(text.trim());
            onCreated();
        } catch (error) {
            console.error("Error creating consultation:", error);
            alert('Error al crear consulta');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content p-6" onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Nueva Consulta Manual</h3>
                    <button onClick={onClose} style={{ color: 'var(--color-text-muted)' }}>
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                            Texto de la consulta
                        </label>
                        <textarea
                            value={text}
                            onChange={e => setText(e.target.value)}
                            className="input min-h-[200px] resize-y"
                            placeholder="Ingrese el texto medico: motivo de consulta, sintomas, hallazgos, diagnostico, plan de tratamiento..."
                            required
                        />
                    </div>

                    <div className="flex gap-2 justify-end">
                        <button type="button" onClick={onClose} className="btn btn-outline">Cancelar</button>
                        <button type="submit" disabled={submitting || !text.trim()} className="btn btn-primary">
                            {submitting ? 'Procesando...' : 'Crear Consulta'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TextNoteModal;
