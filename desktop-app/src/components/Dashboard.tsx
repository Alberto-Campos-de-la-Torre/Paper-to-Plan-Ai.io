import React, { useEffect, useState } from 'react';
import { getNotes, Note, getStats } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { Clock, Activity, Search, BarChart3, MoreHorizontal, Timer, Hourglass } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, Cell, PieChart as RePieChart, Pie } from 'recharts';

interface DashboardProps {
    activeFilter?: string;
    showCompleted?: boolean;
    currentUser?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ activeFilter = 'all', showCompleted = false, currentUser = 'Beto May' }) => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        loadData();
    }, [currentUser]);

    const loadData = async () => {
        try {
            const [notesData, statsData] = await Promise.all([getNotes(), getStats()]);
            setNotes(notesData);
            setStats(statsData);
        } catch (error) {
            console.error("Error loading data:", error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return 'text-green-400 bg-green-400/10 border-green-400/20';
            case 'processing': return 'text-cyan-400 bg-cyan-400/10 border-cyan-400/20';
            case 'error': return 'text-red-400 bg-red-400/10 border-red-400/20';
            default: return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'completed': return 'INDEXED';
            case 'processing': return 'PROCESSING';
            case 'error': return 'ERROR';
            default: return 'IN PROGRESS';
        }
    };

    // Filter Logic
    const filteredNotes = notes.filter(note => {
        if (searchTerm && !note.title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
        if (!showCompleted && note.status === 'completed') return false;
        if (activeFilter !== 'all') {
            const timeLower = (note.implementation_time || '').toLowerCase();
            if (activeFilter === 'Corto Plazo') {
                if (!timeLower.includes('corto')) return false;
            } else if (activeFilter === 'Mediano Plazo') {
                if (!timeLower.includes('mediano') && !timeLower.includes('medio')) return false;
            } else if (activeFilter === 'Largo Plazo') {
                if (!timeLower.includes('largo')) return false;
            }
        }
        return true;
    });

    return (
        <div className="h-full overflow-y-auto px-8 py-8 bg-black relative font-mono">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-blue-950/10 to-transparent pointer-events-none" />

            {/* Header */}
            <div className="relative z-10 flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-white mb-1 tracking-tight font-display">Dashboard</h2>
                    <p className="text-gray-400 text-sm">Bienvenido de nuevo, <span className="text-cyan-400 font-semibold">{currentUser}</span>.</p>
                </div>

                <div className="flex items-center gap-6 text-xs text-gray-500 font-mono">
                    <div className="flex items-center gap-2">
                        <Hourglass className="w-4 h-4" />
                        <span>PROGRESO</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Timer className="w-4 h-4" />
                        <span>TIEMPOS</span>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="relative z-10 mb-8">
                <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Buscar proyectos..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full bg-[#1a1b26] border border-gray-800 text-gray-200 pl-10 pr-4 py-3 rounded-lg focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all placeholder-gray-600 text-sm font-mono"
                    />
                </div>
            </div>

            {/* Projects List */}
            <div className="relative z-10 space-y-6">
                {loading ? (
                    <div className="text-center py-20 text-gray-500 animate-pulse">Cargando proyectos...</div>
                ) : filteredNotes.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No se encontraron proyectos</div>
                ) : (
                    filteredNotes.map((note) => (
                        <div
                            key={note.id}
                            onClick={() => navigate(`/note/${note.id}`)}
                            className="group bg-[#111827] border border-gray-800 hover:border-cyan-500/50 p-6 rounded-xl transition-all duration-300 cursor-pointer relative overflow-hidden shadow-lg hover:shadow-cyan-900/20"
                        >
                            <div className="flex justify-between items-start mb-3">
                                <div className="flex-1 pr-4">
                                    <h3 className="text-lg font-bold text-gray-100 group-hover:text-cyan-400 transition-colors line-clamp-1 font-display">
                                        {note.title || 'Sin Título'}
                                    </h3>
                                    <p className="text-xs text-gray-500 mt-1 line-clamp-1 font-mono">
                                        Proyecto generado por IA. Haz clic para ver detalles.
                                    </p>
                                </div>

                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <span className="text-lg font-bold text-white font-mono">{note.feasibility_score}%</span>
                                        <div className="w-20 h-1 bg-gray-800 rounded-full mt-1 overflow-hidden">
                                            <div
                                                className="h-full bg-cyan-500 rounded-full"
                                                style={{ width: `${note.feasibility_score}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                    <button className="text-gray-600 group-hover:text-cyan-400 transition-colors">
                                        <MoreHorizontal className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex items-center gap-4 text-[10px] text-gray-500 font-mono uppercase tracking-wider">
                                <div className="flex items-center gap-1.5">
                                    <Clock className="w-3 h-3" />
                                    <span>{note.implementation_time || 'N/A'}</span>
                                </div>

                                <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${getStatusColor(note.status)}`}>
                                    {getStatusLabel(note.status)}
                                </span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Dashboard;
