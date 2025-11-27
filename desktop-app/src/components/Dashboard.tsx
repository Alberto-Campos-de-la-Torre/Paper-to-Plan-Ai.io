import React, { useEffect, useState } from 'react';
import { getNotes, Note } from '../api/client';
import { useNavigate } from 'react-router-dom';

interface DashboardProps {
    activeFilter?: string;
    showCompleted?: boolean;
    currentUser?: string;
}

const Dashboard: React.FC<DashboardProps> = ({ activeFilter = 'all', showCompleted = false, currentUser = 'Beto May' }) => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        loadData();
    }, [currentUser]);

    const loadData = async () => {
        try {
            const notesData = await getNotes();
            setNotes(notesData);
        } catch (error) {
            console.error("Error loading data:", error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed': return 'bg-green-200 dark:bg-green-800 text-green-800 dark:text-green-200';
            case 'processing': return 'bg-cyan-200 dark:bg-cyan-800 text-cyan-800 dark:text-cyan-200';
            case 'error': return 'bg-red-200 dark:bg-red-800 text-red-800 dark:text-red-200';
            default: return 'bg-yellow-200 dark:bg-yellow-800 text-yellow-800 dark:text-yellow-200';
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
        <main className="flex-1 flex flex-col p-8 overflow-y-auto bg-background-light dark:bg-background-dark text-gray-800 dark:text-gray-200 font-mono">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
                    <p className="text-gray-600 dark:text-gray-400">Bienvenido de nuevo, {currentUser}.</p>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-2">
                        <span className="material-icons-outlined">hourglass_top</span>
                        <span>PROGRESO</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="material-icons-outlined">timer</span>
                        <span>TIEMPOS</span>
                    </div>
                </div>
            </header>

            <div className="relative mb-8">
                <input
                    type="search"
                    placeholder="Buscar proyectos..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 rounded border border-gray-300 dark:border-gray-700 bg-background-light dark:bg-gray-900 focus:ring-2 focus:ring-primary focus:border-primary placeholder-gray-500 dark:placeholder-gray-400"
                />
                <span className="material-icons-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">search</span>
            </div>

            <div className="space-y-6">
                {loading ? (
                    <div className="text-center py-20 text-gray-500">Cargando proyectos...</div>
                ) : filteredNotes.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No se encontraron proyectos</div>
                ) : (
                    filteredNotes.map((note) => (
                        <div
                            key={note.id}
                            onClick={() => navigate(`/note/${note.id}`)}
                            className="bg-gray-100 dark:bg-gray-900/50 p-6 rounded border border-gray-300 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-all duration-300 group cursor-pointer"
                        >
                            <div className="flex justify-between items-start">
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{note.title || 'Sin Título'}</h3>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Proyecto generado por IA. Haz clic para ver los detalles completos y el plan de implementación.</p>
                                </div>
                                <div className="flex items-center gap-4 ml-4">
                                    <div className="text-right">
                                        <span className="text-lg font-bold text-gray-900 dark:text-white">{note.feasibility_score}%</span>
                                        <div className="w-20 h-1 bg-gray-300 dark:bg-gray-700 rounded-full mt-1">
                                            <div className="h-1 bg-primary rounded-full" style={{ width: `${note.feasibility_score}%` }}></div>
                                        </div>
                                    </div>
                                    <button className="text-gray-500 dark:text-gray-400 group-hover:text-primary transition-colors">
                                        <span className="material-icons-outlined">more_horiz</span>
                                    </button>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                                <div className="flex items-center gap-2">
                                    <span className="material-icons-outlined">schedule</span>
                                    <span>{note.implementation_time?.toUpperCase() || 'N/A'}</span>
                                </div>
                                <span className={`px-2 py-0.5 rounded-full ${getStatusColor(note.status)}`}>{getStatusLabel(note.status)}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </main>
    );
};

export default Dashboard;
