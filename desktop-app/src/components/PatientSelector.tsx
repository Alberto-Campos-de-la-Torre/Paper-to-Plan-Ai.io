import React, { useState, useEffect } from 'react';
import { X, Search } from 'lucide-react';
import { searchPatients, linkPatient, Patient } from '../api/client';

interface PatientSelectorProps {
    consultationId: number;
    onClose: () => void;
    onLinked: () => void;
}

const PatientSelector: React.FC<PatientSelectorProps> = ({ consultationId, onClose, onLinked }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => {
            if (query.length >= 2) doSearch();
            else setResults([]);
        }, 300);
        return () => clearTimeout(timer);
    }, [query]);

    const doSearch = async () => {
        setLoading(true);
        try {
            const data = await searchPatients(query);
            setResults(data);
        } catch (error) {
            console.error("Error searching patients:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = async (patientId: number) => {
        try {
            await linkPatient(consultationId, patientId);
            onLinked();
        } catch (error) {
            console.error("Error linking patient:", error);
            alert('Error al vincular paciente');
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content p-6" onClick={e => e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Vincular Paciente</h3>
                    <button onClick={onClose} style={{ color: 'var(--color-text-muted)' }}>
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="relative mb-4">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
                    <input
                        type="text"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        className="input pl-10"
                        placeholder="Buscar paciente por nombre..."
                        autoFocus
                    />
                </div>

                <div className="max-h-[300px] overflow-y-auto space-y-2">
                    {loading && <p className="text-sm text-center py-4" style={{ color: 'var(--color-text-muted)' }}>Buscando...</p>}
                    {!loading && query.length >= 2 && results.length === 0 && (
                        <p className="text-sm text-center py-4" style={{ color: 'var(--color-text-muted)' }}>No se encontraron pacientes</p>
                    )}
                    {results.map(p => (
                        <button
                            key={p.id}
                            onClick={() => handleSelect(p.id)}
                            className="w-full flex items-center gap-3 p-3 rounded-lg text-left transition-colors"
                            style={{ background: 'var(--color-surface-alt)', border: '1px solid var(--color-border-light)' }}
                        >
                            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold"
                                 style={{ background: 'var(--color-primary)' }}>
                                {p.name.charAt(0)}
                            </div>
                            <div>
                                <p className="font-medium text-sm">{p.name}</p>
                                <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                                    {p.gender || ''} {p.blood_type ? `| ${p.blood_type}` : ''}
                                </p>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default PatientSelector;
