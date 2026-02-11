import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
    getConsultationDetail, deleteConsultation, regenerateConsultation,
    markReviewed, downloadMedicalNote, downloadPrescription,
    ConsultationDetail as ConsultationDetailType
} from '../api/client';
import {
    ArrowLeft, Trash2, RefreshCw, CheckCircle, Download, Edit3,
    Stethoscope, Pill, FlaskConical, Heart, FileText, Link2
} from 'lucide-react';
import PatientSelector from './PatientSelector';
import MedicalTags from './MedicalTags';

const ConsultationDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [data, setData] = useState<ConsultationDetailType | null>(null);
    const [loading, setLoading] = useState(true);
    const [rawText, setRawText] = useState('');
    const [isRegenerating, setIsRegenerating] = useState(false);
    const [activeTab, setActiveTab] = useState<'nota' | 'receta' | 'lab' | 'referencias'>('nota');
    const [showLinkPatient, setShowLinkPatient] = useState(false);

    useEffect(() => {
        if (id) loadConsultation(parseInt(id));
    }, [id]);

    const loadConsultation = async (cId: number) => {
        try {
            const result = await getConsultationDetail(cId);
            setData(result);
            setRawText(result.raw_text || '');
        } catch (error) {
            console.error("Error loading consultation:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!data || !window.confirm('Eliminar esta consulta?')) return;
        try {
            await deleteConsultation(data.id);
            navigate('/');
        } catch (error) {
            console.error("Error:", error);
            alert('Error al eliminar');
        }
    };

    const handleRegenerate = async () => {
        if (!data) return;
        setIsRegenerating(true);
        try {
            await regenerateConsultation(data.id, rawText);
            setTimeout(() => loadConsultation(data.id), 2000);
        } catch (error) {
            console.error("Error:", error);
            alert('Error al regenerar');
        } finally {
            setIsRegenerating(false);
        }
    };

    const handleMarkReviewed = async () => {
        if (!data) return;
        try {
            await markReviewed(data.id);
            await loadConsultation(data.id);
        } catch (error) {
            console.error("Error:", error);
        }
    };

    const handleDownloadNote = async () => {
        if (!data) return;
        try {
            const blob = await downloadMedicalNote(data.id);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `nota_medica_${data.id}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error:", error);
            alert('Error al descargar nota medica');
        }
    };

    const handleDownloadPrescription = async () => {
        if (!data) return;
        try {
            const blob = await downloadPrescription(data.id);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `receta_${data.id}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error:", error);
            alert('Error al descargar receta');
        }
    };

    const handlePatientLinked = () => {
        setShowLinkPatient(false);
        if (data) loadConsultation(data.id);
    };

    if (loading) return (
        <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-10 w-10" style={{ border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)' }} />
        </div>
    );

    if (!data) return <div className="p-8">Consulta no encontrada</div>;

    const analysis = data.ai_analysis || {};
    const subj = analysis.subjective || {};
    const obj = analysis.objective || {};
    const assess = analysis.assessment || {};
    const plan = analysis.plan || {};

    const getStatusClass = (s: string) => {
        switch (s) {
            case 'reviewed': return 'tag-status tag-status-reviewed';
            case 'processed': return 'tag-status tag-status-processed';
            case 'processing': return 'tag-status tag-status-processing';
            case 'error': return 'tag-status tag-status-error';
            default: return 'tag-status tag-status-pending';
        }
    };

    return (
        <div className="h-full overflow-y-auto">
            <div className="p-6 max-w-5xl mx-auto space-y-5">
                {/* Header */}
                <header className="flex justify-between items-center">
                    <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm"
                            style={{ color: 'var(--color-text-muted)' }}>
                        <ArrowLeft className="w-4 h-4" />
                        VOLVER
                    </button>
                    <span className={getStatusClass(data.status)}>
                        {data.status === 'reviewed' ? 'REVISADO' : data.status === 'processed' ? 'PROCESADO' : data.status.toUpperCase()}
                    </span>
                </header>

                {/* Patient Info */}
                {data.patient ? (
                    <div className="card p-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                                     style={{ background: 'var(--color-primary)' }}>
                                    {data.patient.name.charAt(0)}
                                </div>
                                <div>
                                    <p className="font-semibold">{data.patient.name}</p>
                                    <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-muted)' }}>
                                        {data.patient.gender && <span>{data.patient.gender}</span>}
                                        {data.patient.blood_type && <span>| {data.patient.blood_type}</span>}
                                    </div>
                                </div>
                            </div>
                            <button onClick={() => navigate(`/patients/${data.patient!.id}`)} className="btn btn-sm btn-outline">
                                Ver Paciente
                            </button>
                        </div>
                        {data.patient.allergies.length > 0 && (
                            <div className="mt-3 flex flex-wrap gap-1">
                                <MedicalTags items={data.patient.allergies} type="allergy" />
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="card p-4 flex items-center justify-between">
                        <span className="text-sm" style={{ color: 'var(--color-text-muted)' }}>Sin paciente vinculado</span>
                        <button onClick={() => setShowLinkPatient(true)} className="btn btn-sm btn-outline">
                            <Link2 className="w-3 h-3" /> Vincular Paciente
                        </button>
                    </div>
                )}

                {/* Summary */}
                {analysis.summary && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-2 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                            <FileText className="w-4 h-4" /> Resumen
                        </h3>
                        <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                            {analysis.summary}
                        </p>
                        {analysis.confidence_score !== undefined && (
                            <div className="mt-3 flex items-center gap-2">
                                <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Confianza:</span>
                                <div className="confidence-bar flex-1" style={{ maxWidth: '120px' }}>
                                    <div className="confidence-bar-fill"
                                         style={{
                                             width: `${analysis.confidence_score}%`,
                                             background: analysis.confidence_score >= 70 ? 'var(--color-success)' : 'var(--color-warning)'
                                         }} />
                                </div>
                                <span className="text-xs font-mono" style={{ color: 'var(--color-text-muted)' }}>{analysis.confidence_score}%</span>
                            </div>
                        )}
                    </div>
                )}

                {/* SOAP Tabs */}
                <div className="flex gap-1 p-1 rounded-lg" style={{ background: 'var(--color-surface)' }}>
                    {(['nota', 'receta', 'lab', 'referencias'] as const).map(tab => (
                        <button key={tab} onClick={() => setActiveTab(tab)}
                                className="flex-1 py-2 px-3 rounded-md text-xs font-semibold uppercase transition-all"
                                style={{
                                    background: activeTab === tab ? 'var(--color-primary)' : 'transparent',
                                    color: activeTab === tab ? '#ffffff' : 'var(--color-text-muted)',
                                }}>
                            {tab === 'nota' ? 'Nota SOAP' : tab === 'receta' ? 'Receta' : tab === 'lab' ? 'Laboratorio' : 'Referencias'}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                {activeTab === 'nota' && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                        {/* Subjective */}
                        <div className="card p-5">
                            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                                <Stethoscope className="w-4 h-4" /> Subjetivo
                            </h3>
                            {subj.chief_complaint && (
                                <div className="mb-2">
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Motivo de consulta:</span>
                                    <p className="text-sm">{subj.chief_complaint}</p>
                                </div>
                            )}
                            {subj.symptoms && subj.symptoms.length > 0 && (
                                <div className="mb-2">
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Sintomas:</span>
                                    <p className="text-sm">{subj.symptoms.join(', ')}</p>
                                </div>
                            )}
                            {subj.history && (
                                <div>
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Antecedentes:</span>
                                    <p className="text-sm">{subj.history}</p>
                                </div>
                            )}
                        </div>

                        {/* Objective */}
                        <div className="card p-5">
                            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                                <Heart className="w-4 h-4" /> Objetivo
                            </h3>
                            {obj.vitals && (
                                <div className="grid grid-cols-2 gap-2 mb-3">
                                    {Object.entries(obj.vitals).map(([k, v]) => v ? (
                                        <div key={k} className="p-2 rounded text-xs" style={{ background: 'var(--color-surface-alt)' }}>
                                            <span style={{ color: 'var(--color-text-muted)' }}>{k}:</span>
                                            <span className="ml-1 font-medium">{v}</span>
                                        </div>
                                    ) : null)}
                                </div>
                            )}
                            {obj.findings && obj.findings.length > 0 && (
                                <div>
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Hallazgos:</span>
                                    <ul className="text-sm list-disc list-inside mt-1">
                                        {obj.findings.map((f, i) => <li key={i}>{f}</li>)}
                                    </ul>
                                </div>
                            )}
                        </div>

                        {/* Assessment */}
                        <div className="card p-5">
                            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                                Evaluacion
                            </h3>
                            {assess.diagnoses && assess.diagnoses.length > 0 && (
                                <div className="space-y-2 mb-3">
                                    {assess.diagnoses.map((dx, i) => (
                                        <div key={i} className="flex items-center gap-2">
                                            <span className="text-sm">{dx.description}</span>
                                            {dx.cie10_code && <span className="tag tag-cie10">{dx.cie10_code}</span>}
                                        </div>
                                    ))}
                                </div>
                            )}
                            {assess.differential_diagnoses && assess.differential_diagnoses.length > 0 && (
                                <div>
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Diferenciales:</span>
                                    <p className="text-sm">{assess.differential_diagnoses.join(', ')}</p>
                                </div>
                            )}
                        </div>

                        {/* Plan */}
                        <div className="card p-5">
                            <h3 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                                Plan
                            </h3>
                            {plan.follow_up && (
                                <div className="mb-2">
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Seguimiento:</span>
                                    <p className="text-sm">{plan.follow_up}</p>
                                </div>
                            )}
                            {plan.recommendations && plan.recommendations.length > 0 && (
                                <div>
                                    <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Recomendaciones:</span>
                                    <ul className="text-sm list-disc list-inside mt-1">
                                        {plan.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'receta' && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                            <Pill className="w-4 h-4" /> Medicamentos
                        </h3>
                        {(plan.medications && plan.medications.length > 0) ? (
                            <div className="space-y-3">
                                {plan.medications.map((med, i) => (
                                    <div key={i} className="p-3 rounded-lg" style={{ background: 'var(--color-surface-alt)', border: '1px solid var(--color-border-light)' }}>
                                        <p className="font-semibold text-sm">{med.drug_name}</p>
                                        <div className="flex flex-wrap gap-3 mt-1 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                                            {med.dose && <span>Dosis: {med.dose}</span>}
                                            {med.frequency && <span>Frecuencia: {med.frequency}</span>}
                                            {med.duration && <span>Duracion: {med.duration}</span>}
                                        </div>
                                        {med.instructions && <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>{med.instructions}</p>}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>No hay medicamentos registrados</p>
                        )}
                    </div>
                )}

                {activeTab === 'lab' && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                            <FlaskConical className="w-4 h-4" /> Laboratorio
                        </h3>
                        {(analysis.lab_values && analysis.lab_values.length > 0) ? (
                            <div className="overflow-x-auto">
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
                                        {analysis.lab_values.map((lab, i) => (
                                            <tr key={i} style={{ borderBottom: '1px solid var(--color-border-light)' }}>
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
                            </div>
                        ) : (
                            <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>No hay resultados de laboratorio</p>
                        )}
                    </div>
                )}

                {activeTab === 'referencias' && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--color-primary)' }}>Referencias y Estudios</h3>
                        {plan.referrals && plan.referrals.length > 0 ? (
                            <div className="mb-3">
                                <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Referencias:</span>
                                <ul className="text-sm list-disc list-inside mt-1">
                                    {plan.referrals.map((r, i) => <li key={i}>{r}</li>)}
                                </ul>
                            </div>
                        ) : null}
                        {plan.studies && plan.studies.length > 0 ? (
                            <div>
                                <span className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>Estudios solicitados:</span>
                                <ul className="text-sm list-disc list-inside mt-1">
                                    {plan.studies.map((s, i) => <li key={i}>{s}</li>)}
                                </ul>
                            </div>
                        ) : null}
                        {(!plan.referrals || plan.referrals.length === 0) && (!plan.studies || plan.studies.length === 0) && (
                            <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>No hay referencias ni estudios</p>
                        )}
                    </div>
                )}

                {/* Raw Text */}
                <div className="card p-5">
                    <h3 className="text-sm font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--color-primary)' }}>
                        <Edit3 className="w-4 h-4" /> Texto Extraido
                    </h3>
                    <textarea
                        value={rawText}
                        onChange={e => setRawText(e.target.value)}
                        className="input min-h-[100px] resize-y font-mono text-sm"
                        placeholder="Texto extraido..."
                    />
                </div>

                {/* Actions */}
                <footer className="flex flex-wrap gap-2 pt-2 pb-6">
                    <button onClick={handleDelete} className="btn btn-sm btn-outline" style={{ color: 'var(--color-error)' }}>
                        <Trash2 className="w-3 h-3" /> ELIMINAR
                    </button>
                    <button onClick={handleRegenerate} disabled={isRegenerating} className="btn btn-sm btn-outline">
                        <RefreshCw className={`w-3 h-3 ${isRegenerating ? 'animate-spin' : ''}`} />
                        {isRegenerating ? 'REGENERANDO...' : 'REGENERAR'}
                    </button>
                    <button onClick={handleMarkReviewed} className="btn btn-sm btn-primary">
                        <CheckCircle className="w-3 h-3" /> MARCAR REVISADO
                    </button>
                    <div className="flex-1" />
                    <button onClick={handleDownloadNote} className="btn btn-sm btn-accent">
                        <Download className="w-3 h-3" /> NOTA PDF
                    </button>
                    <button onClick={handleDownloadPrescription} className="btn btn-sm btn-outline">
                        <Download className="w-3 h-3" /> RECETA PDF
                    </button>
                </footer>
            </div>

            {/* Link Patient Modal */}
            {showLinkPatient && data && (
                <PatientSelector consultationId={data.id} onClose={() => setShowLinkPatient(false)} onLinked={handlePatientLinked} />
            )}
        </div>
    );
};

export default ConsultationDetail;
