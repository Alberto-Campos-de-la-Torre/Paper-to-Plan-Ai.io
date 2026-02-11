import React, { useEffect, useState } from 'react';
import { getConsultations, Consultation } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { Search, FileText, Stethoscope, FlaskConical, Pill } from 'lucide-react';

interface DashboardProps {
    activeFilter?: string;
    showReviewed?: boolean;
    currentUser?: string;
    refreshKey?: number;
}

const Dashboard: React.FC<DashboardProps> = ({ activeFilter = 'all', showReviewed = false, currentUser = '', refreshKey = 0 }) => {
    const [consultations, setConsultations] = useState<Consultation[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        loadData();
    }, [currentUser, refreshKey]);

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

    const getStatusClass = (status: string) => {
        switch (status) {
            case 'reviewed': return 'tag-status tag-status-reviewed';
            case 'processed': return 'tag-status tag-status-processed';
            case 'processing': return 'tag-status tag-status-processing';
            case 'error': return 'tag-status tag-status-error';
            default: return 'tag-status tag-status-pending';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'reviewed': return 'REVISADO';
            case 'processed': return 'PROCESADO';
            case 'processing': return 'PROCESANDO';
            case 'error': return 'ERROR';
            default: return 'PENDIENTE';
        }
    };

    const getDocTypeIcon = (type: string) => {
        switch (type) {
            case 'prescription': return <Pill className="w-4 h-4" />;
            case 'lab_result': return <FlaskConical className="w-4 h-4" />;
            case 'referral': return <FileText className="w-4 h-4" />;
            default: return <Stethoscope className="w-4 h-4" />;
        }
    };

    const getDocTypeLabel = (type: string) => {
        switch (type) {
            case 'prescription': return 'Receta';
            case 'lab_result': return 'Laboratorio';
            case 'referral': return 'Referencia';
            default: return 'Consulta';
        }
    };

    const getConfidenceColor = (score: number) => {
        if (score >= 80) return 'var(--color-success)';
        if (score >= 60) return 'var(--color-info)';
        if (score >= 40) return 'var(--color-warning)';
        return 'var(--color-error)';
    };

    const filtered = consultations.filter(c => {
        if (searchTerm && !c.summary.toLowerCase().includes(searchTerm.toLowerCase())) return false;
        if (!showReviewed && c.status === 'reviewed') return false;
        if (activeFilter !== 'all' && c.document_type !== activeFilter) return false;
        return true;
    });

    return (
        <div className="h-full overflow-y-auto px-8 py-8">
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>Expedientes</h2>
                    <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                        Bienvenido, <span className="font-semibold" style={{ color: 'var(--color-accent)' }}>{currentUser}</span>
                    </p>
                </div>
                <div className="text-sm font-mono" style={{ color: 'var(--color-text-muted)' }}>
                    {filtered.length} registro{filtered.length !== 1 ? 's' : ''}
                </div>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-text-muted)' }} />
                <input
                    type="text"
                    placeholder="Buscar consultas..."
                    value={searchTerm}
                    onChange={e => setSearchTerm(e.target.value)}
                    className="input pl-10"
                />
            </div>

            {/* List */}
            <div className="space-y-3">
                {loading ? (
                    <div className="text-center py-20" style={{ color: 'var(--color-text-muted)' }}>
                        <div className="animate-spin rounded-full h-8 w-8 mx-auto mb-3" style={{ border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)' }} />
                        Cargando expedientes...
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-20" style={{ color: 'var(--color-text-muted)' }}>
                        No se encontraron expedientes
                    </div>
                ) : (
                    filtered.map((c, i) => (
                        <div
                            key={c.id}
                            onClick={() => navigate(`/consultation/${c.id}`)}
                            className="card card-interactive p-5 cursor-pointer animate-fade-in"
                            style={{ animationDelay: `${i * 50}ms` }}
                        >
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex-1 pr-4">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span style={{ color: 'var(--color-accent)' }}>{getDocTypeIcon(c.document_type)}</span>
                                        <span className="text-xs font-semibold uppercase" style={{ color: 'var(--color-accent)' }}>
                                            {getDocTypeLabel(c.document_type)}
                                        </span>
                                    </div>
                                    <p className="text-sm leading-relaxed line-clamp-2" style={{ color: 'var(--color-text)' }}>
                                        {c.summary || 'Sin resumen disponible'}
                                    </p>
                                </div>

                                <div className="flex flex-col items-end gap-2">
                                    <span className={getStatusClass(c.status)}>
                                        {getStatusLabel(c.status)}
                                    </span>
                                    {c.confidence_score > 0 && (
                                        <div className="flex items-center gap-2">
                                            <span className="text-xs font-mono" style={{ color: 'var(--color-text-muted)' }}>
                                                {c.confidence_score}%
                                            </span>
                                            <div className="confidence-bar" style={{ width: '48px' }}>
                                                <div
                                                    className="confidence-bar-fill"
                                                    style={{ width: `${c.confidence_score}%`, background: getConfidenceColor(c.confidence_score) }}
                                                />
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="flex items-center gap-3 text-xs" style={{ color: 'var(--color-text-muted)' }}>
                                {c.created_at && (
                                    <span>{new Date(c.created_at).toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Dashboard;
