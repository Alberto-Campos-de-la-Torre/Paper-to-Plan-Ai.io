import React, { useEffect, useState } from 'react';
import { getConsultations, Consultation } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { Stethoscope, Pill, FlaskConical, FileText } from 'lucide-react';

interface KanbanProps {
    currentUser?: string;
    showReviewed?: boolean;
}

const Kanban: React.FC<KanbanProps> = ({ currentUser = '', showReviewed = false }) => {
    const [consultations, setConsultations] = useState<Consultation[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        loadData();
    }, [currentUser]);

    const loadData = async () => {
        try {
            const data = await getConsultations();
            setConsultations(data);
        } catch (error) {
            console.error("Error loading consultations:", error);
        } finally {
            setLoading(false);
        }
    };

    const columns = [
        { id: 'pending', title: 'Pendientes', color: '#b8860b' },
        { id: 'processing', title: 'En Proceso', color: '#2471a3' },
        { id: 'processed', title: 'Procesados', color: '#2d6a2d' },
        { id: 'reviewed', title: 'Revisados', color: '#7c3aed' },
    ];

    const getBuckets = () => {
        const buckets: Record<string, Consultation[]> = { pending: [], processing: [], processed: [], reviewed: [] };
        consultations.forEach(c => {
            if (!showReviewed && c.status === 'reviewed') return;
            const key = c.status === 'error' ? 'pending' : c.status;
            if (buckets[key]) buckets[key].push(c);
            else buckets.pending.push(c);
        });
        return buckets;
    };

    const getDocTypeIcon = (type: string) => {
        switch (type) {
            case 'prescription': return <Pill className="w-3.5 h-3.5" />;
            case 'lab_result': return <FlaskConical className="w-3.5 h-3.5" />;
            case 'referral': return <FileText className="w-3.5 h-3.5" />;
            default: return <Stethoscope className="w-3.5 h-3.5" />;
        }
    };

    const getDocTypeLabel = (type: string) => {
        switch (type) {
            case 'prescription': return 'Receta';
            case 'lab_result': return 'Lab';
            case 'referral': return 'Referencia';
            default: return 'Consulta';
        }
    };

    const buckets = getBuckets();

    return (
        <div className="h-full overflow-x-auto p-8">
            <div className="mb-6">
                <h2 className="text-2xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>Tablero</h2>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                    Gestiona expedientes por estado de procesamiento
                </p>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8" style={{ border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)' }} />
                </div>
            ) : (
                <div className="flex gap-4 h-[calc(100%-80px)] min-w-[1000px]">
                    {columns.map(col => (
                        <div key={col.id} className="flex-1 flex flex-col min-w-[240px] rounded-xl overflow-hidden"
                             style={{ background: 'var(--color-surface)', border: '1px solid var(--color-border-light)' }}>
                            {/* Column Header */}
                            <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                                <div className="flex items-center gap-2">
                                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: col.color }} />
                                    <span className="font-semibold text-sm">{col.title}</span>
                                    <span className="text-xs px-1.5 py-0.5 rounded font-mono"
                                          style={{ background: 'var(--color-surface-alt)', color: 'var(--color-text-muted)' }}>
                                        {buckets[col.id].length}
                                    </span>
                                </div>
                            </div>

                            {/* Cards */}
                            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                                {buckets[col.id].map(c => (
                                    <div
                                        key={c.id}
                                        onClick={() => navigate(`/consultation/${c.id}`)}
                                        className="p-3 rounded-lg cursor-pointer transition-all hover:shadow-md"
                                        style={{ background: 'var(--color-surface-alt)', border: '1px solid var(--color-border-light)' }}
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            <span style={{ color: 'var(--color-accent)' }}>{getDocTypeIcon(c.document_type)}</span>
                                            <span className="text-[10px] font-semibold uppercase" style={{ color: 'var(--color-accent)' }}>
                                                {getDocTypeLabel(c.document_type)}
                                            </span>
                                        </div>
                                        <p className="text-xs line-clamp-2 mb-2" style={{ color: 'var(--color-text)' }}>
                                            {c.summary || 'Sin resumen'}
                                        </p>
                                        {c.confidence_score > 0 && (
                                            <div className="confidence-bar">
                                                <div className="confidence-bar-fill"
                                                     style={{
                                                         width: `${c.confidence_score}%`,
                                                         background: c.confidence_score >= 70 ? 'var(--color-success)' : c.confidence_score >= 40 ? 'var(--color-warning)' : 'var(--color-error)'
                                                     }} />
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Kanban;
