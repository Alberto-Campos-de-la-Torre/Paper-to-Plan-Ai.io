import React, { useEffect, useState } from 'react';
import { getStats, MedicalStats } from '../api/client';
import { PieChart as RePieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface StatisticsProps {
    currentUser?: string;
}

const COLORS = ['#2d3b2d', '#8b7355', '#2471a3', '#b8860b', '#7c3aed', '#c0392b'];

const Statistics: React.FC<StatisticsProps> = ({ currentUser = '' }) => {
    const [stats, setStats] = useState<MedicalStats | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, [currentUser]);

    const loadStats = async () => {
        try {
            const data = await getStats();
            setStats(data);
        } catch (error) {
            console.error("Error loading stats:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8" style={{ border: '2px solid var(--color-border)', borderTopColor: 'var(--color-primary)' }} />
        </div>
    );

    if (!stats) return <div className="p-8">Error al cargar estadisticas</div>;

    const docTypeLabels: Record<string, string> = {
        consultation: 'Consultas',
        prescription: 'Recetas',
        lab_result: 'Laboratorio',
        referral: 'Referencias',
    };

    const docTypeData = Object.entries(stats.document_types).map(([k, v]) => ({
        name: docTypeLabels[k] || k,
        value: v,
    }));

    const statusLabels: Record<string, string> = {
        pending: 'Pendientes',
        processing: 'En Proceso',
        processed: 'Procesados',
        reviewed: 'Revisados',
        error: 'Errores',
    };

    const statusData = Object.entries(stats.consultations_by_status).map(([k, v]) => ({
        name: statusLabels[k] || k,
        value: v,
    }));

    return (
        <div className="h-full overflow-y-auto p-8">
            <div className="mb-6">
                <h2 className="text-2xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>Estadisticas</h2>
                <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>Resumen de actividad del sistema</p>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="card p-5 text-center">
                    <p className="text-3xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>{stats.total_patients}</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>Pacientes</p>
                </div>
                <div className="card p-5 text-center">
                    <p className="text-3xl font-bold font-display" style={{ color: 'var(--color-accent)' }}>{stats.total_consultations}</p>
                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>Consultas</p>
                </div>
                <div className="card p-5 text-center">
                    <p className="text-3xl font-bold font-display" style={{ color: 'var(--color-success)' }}>
                        {stats.consultations_by_status['reviewed'] || 0}
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>Revisados</p>
                </div>
                <div className="card p-5 text-center">
                    <p className="text-3xl font-bold font-display" style={{ color: 'var(--color-warning)' }}>
                        {stats.consultations_by_status['pending'] || 0}
                    </p>
                    <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>Pendientes</p>
                </div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {docTypeData.length > 0 && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--color-primary)' }}>Tipos de Documento</h3>
                        <ResponsiveContainer width="100%" height={250}>
                            <RePieChart>
                                <Pie data={docTypeData} cx="50%" cy="50%" innerRadius={50} outerRadius={90}
                                     paddingAngle={3} dataKey="value" label={({ name, percent }: any) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}>
                                    {docTypeData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip />
                            </RePieChart>
                        </ResponsiveContainer>
                    </div>
                )}

                {statusData.length > 0 && (
                    <div className="card p-5">
                        <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--color-primary)' }}>Estado de Consultas</h3>
                        <ResponsiveContainer width="100%" height={250}>
                            <BarChart data={statusData}>
                                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                                <YAxis tick={{ fontSize: 11 }} />
                                <Tooltip />
                                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                                    {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Statistics;
