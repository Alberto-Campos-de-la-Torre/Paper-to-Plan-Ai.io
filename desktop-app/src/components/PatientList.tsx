import React, { useEffect, useState } from 'react';
import { getPatients, Patient } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { Search, Plus } from 'lucide-react';
import MedicalTags from './MedicalTags';
import PatientFormModal from './PatientFormModal';

const PatientList: React.FC = () => {
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showForm, setShowForm] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        loadPatients();
    }, []);

    const loadPatients = async () => {
        try {
            const data = await getPatients();
            setPatients(data);
        } catch (error) {
            console.error("Error loading patients:", error);
        } finally {
            setLoading(false);
        }
    };

    const filtered = patients.filter(p => {
        if (!searchTerm) return true;
        return p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
               (p.contact_phone || '').includes(searchTerm) ||
               (p.contact_email || '').toLowerCase().includes(searchTerm.toLowerCase());
    });

    return (
        <div className="h-full overflow-y-auto px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>Pacientes</h2>
                    <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                        {patients.length} paciente{patients.length !== 1 ? 's' : ''} registrado{patients.length !== 1 ? 's' : ''}
                    </p>
                </div>
                <button onClick={() => setShowForm(true)} className="btn btn-primary">
                    <Plus className="w-4 h-4" /> Nuevo Paciente
                </button>
            </div>

            <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
                <input
                    type="text"
                    placeholder="Buscar pacientes..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="input pl-10"
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {loading ? (
                    <div className="col-span-full text-center py-20" style={{ color: 'var(--color-text-muted)' }}>
                        Cargando pacientes...
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="col-span-full text-center py-20" style={{ color: 'var(--color-text-muted)' }}>
                        No se encontraron pacientes
                    </div>
                ) : (
                    filtered.map((p, i) => (
                        <div
                            key={p.id}
                            onClick={() => navigate(`/patients/${p.id}`)}
                            className="card card-interactive p-5 cursor-pointer animate-fade-in"
                            style={{ animationDelay: `${i * 30}ms` }}
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                                     style={{ background: 'var(--color-primary)' }}>
                                    {p.name.charAt(0)}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="font-semibold text-sm truncate">{p.name}</p>
                                    <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-muted)' }}>
                                        {p.gender && <span>{p.gender}</span>}
                                        {p.blood_type && <span>| {p.blood_type}</span>}
                                        {p.date_of_birth && <span>| {p.date_of_birth}</span>}
                                    </div>
                                </div>
                            </div>

                            {p.allergies.length > 0 && (
                                <div className="flex flex-wrap gap-1 mb-2">
                                    <MedicalTags items={p.allergies.slice(0, 3)} type="allergy" />
                                    {p.allergies.length > 3 && (
                                        <span className="tag" style={{ background: 'var(--color-surface-alt)', color: 'var(--color-text-muted)' }}>
                                            +{p.allergies.length - 3}
                                        </span>
                                    )}
                                </div>
                            )}

                            {p.conditions.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                    <MedicalTags items={p.conditions.slice(0, 3)} type="condition" />
                                </div>
                            )}

                            {p.contact_phone && (
                                <p className="text-xs mt-2" style={{ color: 'var(--color-text-muted)' }}>{p.contact_phone}</p>
                            )}
                        </div>
                    ))
                )}
            </div>

            {showForm && (
                <PatientFormModal
                    onClose={() => setShowForm(false)}
                    onCreated={() => { setShowForm(false); loadPatients(); }}
                />
            )}
        </div>
    );
};

export default PatientList;
