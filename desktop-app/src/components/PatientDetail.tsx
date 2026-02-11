import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    getPatient, getPatientConsultations, getPatientPrescriptions,
    getPatientLabResults, deletePatient,
    Patient, Consultation, Prescription, LabResult
} from '../api/client';
import { ArrowLeft, Trash2, Edit3, Stethoscope, Pill } from 'lucide-react';
import MedicalTags from './MedicalTags';
import PatientFormModal from './PatientFormModal';

const PatientDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [patient, setPatient] = useState<Patient | null>(null);
    const [consultations, setConsultations] = useState<Consultation[]>([]);
    const [prescriptions, setPrescriptions] = useState<Prescription[]>([]);
    const [labResults, setLabResults] = useState<LabResult[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'historial' | 'laboratorio' | 'recetas' | 'datos'>('historial');
    const [showEditForm, setShowEditForm] = useState(false);

    useEffect(() => {
        if (id) loadAll(parseInt(id));
    }, [id]);

    const loadAll = async (patientId: number) => {
        try {
            const [p, c, rx, lab] = await Promise.all([
                getPatient(patientId),
                getPatientConsultations(patientId),
                getPatientPrescriptions(patientId),
                getPatientLabResults(patientId),
            ]);
            setPatient(p);
            setConsultations(c);
            setPrescriptions(rx);
            setLabResults(lab);
        } catch (error) {
            console.error("Error loading patient:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!patient || !window.confirm(`Eliminar paciente "${patient.name}"?`)) return;
        try {
            await deletePatient(patient.id);
            navigate('/patients');
        } catch (error) {
            console.error("Error:", error);
            alert('Error al eliminar paciente');
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-10 w-10" style={{ border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)' }} />
        </div>
    );

    if (!patient) return <div className="p-8">Paciente no encontrado</div>;

    return (
        <div className="h-full overflow-y-auto">
            <div className="p-6 max-w-5xl mx-auto space-y-5">
                {/* Header */}
                <header className="flex justify-between items-center">
                    <button onClick={() => navigate('/patients')} className="flex items-center gap-2 text-sm"
                            style={{ color: 'var(--color-text-muted)' }}>
                        <ArrowLeft className="w-4 h-4" /> PACIENTES
                    </button>
                    <div className="flex gap-2">
                        <button onClick={() => setShowEditForm(true)} className="btn btn-sm btn-outline">
                            <Edit3 className="w-3 h-3" /> Editar
                        </button>
                        <button onClick={handleDelete} className="btn btn-sm btn-outline" style={{ color: 'var(--color-error)' }}>
                            <Trash2 className="w-3 h-3" /> Eliminar
                        </button>
                    </div>
                </header>

                {/* Patient Info Card */}
                <div className="card p-5">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-14 h-14 rounded-full flex items-center justify-center text-white text-xl font-bold"
                             style={{ background: 'var(--color-primary)' }}>
                            {patient.name.charAt(0)}
                        </div>
                        <div>
                            <h2 className="text-xl font-bold font-display">{patient.name}</h2>
                            <div className="flex items-center gap-3 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                                {patient.gender && <span>{patient.gender}</span>}
                                {patient.date_of_birth && <span>| Nac: {patient.date_of_birth}</span>}
                                {patient.blood_type && <span>| Sangre: {patient.blood_type}</span>}
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-wrap gap-1 mb-2">
                        {patient.allergies.length > 0 && <MedicalTags items={patient.allergies} type="allergy" />}
                    </div>
                    <div className="flex flex-wrap gap-1 mb-2">
                        {patient.conditions.length > 0 && <MedicalTags items={patient.conditions} type="condition" />}
                    </div>
                    <div className="flex flex-wrap gap-1">
                        {patient.cie10_codes.length > 0 && <MedicalTags items={patient.cie10_codes} type="cie10" />}
                    </div>

                    {(patient.contact_phone || patient.contact_email || patient.emergency_contact) && (
                        <div className="mt-3 pt-3 grid grid-cols-3 gap-3 text-xs" style={{ borderTop: '1px solid var(--color-border-light)' }}>
                            {patient.contact_phone && (
                                <div>
                                    <span style={{ color: 'var(--color-text-muted)' }}>Telefono:</span>
                                    <p>{patient.contact_phone}</p>
                                </div>
                            )}
                            {patient.contact_email && (
                                <div>
                                    <span style={{ color: 'var(--color-text-muted)' }}>Email:</span>
                                    <p>{patient.contact_email}</p>
                                </div>
                            )}
                            {patient.emergency_contact && (
                                <div>
                                    <span style={{ color: 'var(--color-text-muted)' }}>Emergencia:</span>
                                    <p>{patient.emergency_contact}</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Tabs */}
                <div className="flex gap-1 p-1 rounded-lg" style={{ background: 'var(--color-surface)' }}>
                    {(['historial', 'laboratorio', 'recetas', 'datos'] as const).map(tab => (
                        <button key={tab} onClick={() => setActiveTab(tab)}
                                className="flex-1 py-2 px-3 rounded-md text-xs font-semibold uppercase transition-all"
                                style={{
                                    background: activeTab === tab ? 'var(--color-primary)' : 'transparent',
                                    color: activeTab === tab ? '#ffffff' : 'var(--color-text-muted)',
                                }}>
                            {tab === 'historial' ? 'Historial' : tab === 'laboratorio' ? 'Laboratorio' : tab === 'recetas' ? 'Recetas' : 'Datos'}
                        </button>
                    ))}
                </div>

                {/* Historial */}
                {activeTab === 'historial' && (
                    <div className="space-y-3">
                        {consultations.length === 0 ? (
                            <p className="text-sm text-center py-8" style={{ color: 'var(--color-text-muted)' }}>Sin consultas registradas</p>
                        ) : consultations.map(c => (
                            <div key={c.id} onClick={() => navigate(`/consultation/${c.id}`)}
                                 className="card card-interactive p-4 cursor-pointer">
                                <div className="flex items-center gap-2 mb-1">
                                    <Stethoscope className="w-3.5 h-3.5" style={{ color: 'var(--color-accent)' }} />
                                    <span className="text-xs font-semibold uppercase" style={{ color: 'var(--color-accent)' }}>
                                        {c.document_type === 'prescription' ? 'Receta' : c.document_type === 'lab_result' ? 'Lab' : 'Consulta'}
                                    </span>
                                    <span className={`tag-status tag-status-${c.status}`}>{c.status.toUpperCase()}</span>
                                </div>
                                <p className="text-sm line-clamp-2">{c.summary || 'Sin resumen'}</p>
                                {c.created_at && (
                                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
                                        {new Date(c.created_at).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Lab Results */}
                {activeTab === 'laboratorio' && (
                    <div className="card p-5">
                        {labResults.length === 0 ? (
                            <p className="text-sm text-center py-8" style={{ color: 'var(--color-text-muted)' }}>Sin resultados de laboratorio</p>
                        ) : (
                            <table className="w-full text-sm">
                                <thead>
                                    <tr style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                                        <th className="text-left py-2 text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Estudio</th>
                                        <th className="text-left py-2 text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Valor</th>
                                        <th className="text-left py-2 text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Unidad</th>
                                        <th className="text-left py-2 text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Referencia</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {labResults.map(lab => (
                                        <tr key={lab.id} style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                                            <td className="py-2">{lab.test_name}</td>
                                            <td className="py-2 font-mono" style={{ color: lab.is_abnormal ? 'var(--color-error)' : 'var(--color-text)' }}>
                                                {lab.value}
                                            </td>
                                            <td className="py-2" style={{ color: 'var(--color-text-muted)' }}>{lab.unit}</td>
                                            <td className="py-2" style={{ color: 'var(--color-text-muted)' }}>{lab.reference_range}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                )}

                {/* Prescriptions */}
                {activeTab === 'recetas' && (
                    <div className="space-y-3">
                        {prescriptions.length === 0 ? (
                            <p className="text-sm text-center py-8" style={{ color: 'var(--color-text-muted)' }}>Sin recetas registradas</p>
                        ) : prescriptions.map(rx => (
                            <div key={rx.id} className="card p-4">
                                <div className="flex items-center gap-2 mb-1">
                                    <Pill className="w-3.5 h-3.5" style={{ color: 'var(--color-accent)' }} />
                                    <span className="font-semibold text-sm">{rx.drug_name}</span>
                                </div>
                                <div className="flex flex-wrap gap-3 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                                    {rx.dose && <span>Dosis: {rx.dose}</span>}
                                    {rx.frequency && <span>Frecuencia: {rx.frequency}</span>}
                                    {rx.duration && <span>Duracion: {rx.duration}</span>}
                                </div>
                                {rx.instructions && <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>{rx.instructions}</p>}
                            </div>
                        ))}
                    </div>
                )}

                {/* Patient Data */}
                {activeTab === 'datos' && (
                    <div className="card p-5 space-y-3 text-sm">
                        <div className="grid grid-cols-2 gap-4">
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Nombre:</span><p>{patient.name}</p></div>
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Nacimiento:</span><p>{patient.date_of_birth || '-'}</p></div>
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Genero:</span><p>{patient.gender || '-'}</p></div>
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Tipo de Sangre:</span><p>{patient.blood_type || '-'}</p></div>
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Telefono:</span><p>{patient.contact_phone || '-'}</p></div>
                            <div><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Email:</span><p>{patient.contact_email || '-'}</p></div>
                            <div className="col-span-2"><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Emergencia:</span><p>{patient.emergency_contact || '-'}</p></div>
                            <div className="col-span-2"><span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Notas:</span><p>{patient.notes || '-'}</p></div>
                        </div>
                    </div>
                )}
            </div>

            {showEditForm && (
                <PatientFormModal
                    patient={patient}
                    onClose={() => setShowEditForm(false)}
                    onCreated={() => { setShowEditForm(false); if (id) loadAll(parseInt(id)); }}
                />
            )}
        </div>
    );
};

export default PatientDetail;
