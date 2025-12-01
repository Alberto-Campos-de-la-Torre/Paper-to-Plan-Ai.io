import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { getStats } from '../api/client';

const Statistics: React.FC = () => {
    const [stats, setStats] = useState<any>(null);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const data = await getStats();
            console.log("Stats loaded:", data);

            // Fix feasibility scores structure if it's just numbers
            if (data.feasibility_scores && data.feasibility_scores.length > 0 && typeof data.feasibility_scores[0] === 'number') {
                data.feasibility_scores = data.feasibility_scores.map((score: number, index: number) => ({
                    name: `Proyecto ${index + 1}`,
                    score: score,
                    full_name: `Proyecto ${index + 1}`
                }));
            }

            setStats(data);
        } catch (error) {
            console.error("Error loading stats:", error);
        }
    };

    if (!stats) return <div className="text-gray-600 dark:text-gray-400 text-center py-8">Cargando estadísticas...</div>;

    const pieData = [
        { name: 'Completados', value: stats.progress.completed },
        { name: 'En Progreso', value: stats.progress.in_progress }
    ];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 className="text-gray-900 dark:text-white text-lg font-bold mb-4">Progreso General</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {pieData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--bg-surface-dark, #1f2937)',
                                    borderColor: 'var(--border-dark, #374151)',
                                    color: '#fff',
                                    borderRadius: '0.5rem'
                                }}
                                itemStyle={{ color: '#fff' }}
                            />
                            <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 className="text-gray-900 dark:text-white text-lg font-bold mb-4">Comparación de Viabilidad</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={stats.feasibility_scores}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:stroke-gray-700" />
                            <XAxis dataKey="name" stroke="#6b7280" className="dark:stroke-gray-400" tick={{ fill: 'currentColor' }} />
                            <YAxis stroke="#6b7280" className="dark:stroke-gray-400" tick={{ fill: 'currentColor' }} />
                            <Tooltip
                                cursor={{ fill: 'rgba(0,0,0,0.1)' }}
                                contentStyle={{
                                    backgroundColor: '#1f2937',
                                    borderColor: '#374151',
                                    color: '#fff',
                                    borderRadius: '0.5rem'
                                }}
                            />
                            <Legend wrapperStyle={{ paddingTop: '20px' }} />
                            <Bar dataKey="score" fill="#82ca9d" name="Puntaje" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default Statistics;
