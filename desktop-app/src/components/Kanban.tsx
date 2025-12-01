import React, { useEffect, useState } from 'react';
import { getNotes, Note } from '../api/client';
import { useNavigate } from 'react-router-dom';
import { MoreHorizontal } from 'lucide-react';

interface KanbanProps {
    currentUser?: string;
    showCompleted?: boolean;
}

const Kanban: React.FC<KanbanProps> = ({ currentUser = 'Beto May', showCompleted = false }) => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        loadNotes();
    }, [currentUser]);

    const loadNotes = async () => {
        try {
            const data = await getNotes();
            setNotes(data);
        } catch (error) {
            console.error("Error loading notes:", error);
        } finally {
            setLoading(false);
        }
    };

    // Define columns structure
    const columns = [
        { id: 'corto', title: 'Corto Plazo', color: 'cyan' },
        { id: 'medio', title: 'Mediano Plazo', color: 'blue' },
        { id: 'largo', title: 'Largo Plazo', color: 'purple' }
    ];

    // Bucket notes based on Tkinter logic
    const getBucketedNotes = () => {
        const buckets: Record<string, Note[]> = {
            corto: [],
            medio: [],
            largo: []
        };

        notes.forEach(note => {
            // Filter by completion status first
            if (!showCompleted && (note.status === 'completed' || note.status === 'Completed')) {
                return;
            }

            const timeEst = (note.implementation_time || '').toLowerCase();

            if (timeEst.includes('corto') || timeEst.includes('short') || timeEst.includes('semana') || timeEst.includes('días') || timeEst.includes('week') || timeEst.includes('day') || timeEst.includes('1 mes') || timeEst.includes('1 month')) {
                buckets.corto.push(note);
            } else if (timeEst.includes('medio') || timeEst.includes('mediano') || timeEst.includes('medium') || timeEst.includes('mes') || timeEst.includes('month')) {
                buckets.medio.push(note);
            } else if (timeEst.includes('largo') || timeEst.includes('long') || timeEst.includes('año') || timeEst.includes('year')) {
                buckets.largo.push(note);
            } else {
                // Default fallback to Short Term (like Tkinter)
                buckets.corto.push(note);
            }
        });

        return buckets;
    };

    const bucketedNotes = getBucketedNotes();

    return (
        <div className="h-full overflow-x-auto p-8 bg-background-light dark:bg-background-dark relative transition-colors duration-300">
            {/* Background Gradients */}
            <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-primary/10 to-transparent pointer-events-none" />

            <div className="relative z-10 mb-8">
                <h2 className="text-3xl font-bold text-text-light dark:text-text-dark tracking-tight font-display">Kanban Board</h2>
                <p className="text-text-secondary-light dark:text-text-secondary-dark">Gestiona tus proyectos por tiempo de implementación.</p>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64">
                    <div className="w-8 h-8 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
                </div>
            ) : (
                <div className="flex gap-6 h-[calc(100%-80px)] min-w-[1000px]">
                    {columns.map(col => (
                        <div key={col.id} className="flex-1 flex flex-col min-w-[300px] bg-surface-light dark:bg-surface-dark rounded-2xl border border-border-light dark:border-border-dark backdrop-blur-sm transition-colors duration-300">
                            {/* Column Header */}
                            <div className={`p-4 border-b border-border-light dark:border-border-dark flex justify-between items-center`}>
                                <div className="flex items-center gap-3">
                                    <div className={`w-3 h-3 rounded-full bg-${col.color}-500 shadow-[0_0_10px_rgba(var(--color-${col.color}),0.5)]`} />
                                    <span className="font-bold text-text-light dark:text-text-dark">{col.title}</span>
                                    <span className="bg-background-light dark:bg-background-dark px-2 py-0.5 rounded text-xs text-text-secondary-light dark:text-text-secondary-dark font-mono">
                                        {bucketedNotes[col.id as keyof typeof bucketedNotes].length}
                                    </span>
                                </div>
                            </div>

                            {/* Column Content */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
                                {bucketedNotes[col.id as keyof typeof bucketedNotes].map(note => (
                                    <div
                                        key={note.id}
                                        onClick={() => navigate(`/note/${note.id}`)}
                                        className="bg-background-light dark:bg-background-dark p-4 rounded-xl border border-border-light dark:border-border-dark hover:border-primary/30 cursor-pointer group transition-all hover:shadow-lg hover:shadow-primary/10"
                                    >
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex items-center gap-2">
                                                {/* User Pin */}
                                                <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center text-[8px] font-bold text-surface-dark shadow-sm ring-1 ring-white/20">
                                                    {currentUser?.substring(0, 2).toUpperCase()}
                                                </div>
                                                <span className="text-[10px] font-bold text-text-secondary-light dark:text-text-secondary-dark uppercase tracking-wider">
                                                    {note.status}
                                                </span>
                                            </div>
                                            <button className="text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark opacity-0 group-hover:opacity-100 transition-opacity">
                                                <MoreHorizontal className="w-4 h-4" />
                                            </button>
                                        </div>
                                        <h4 className="font-semibold text-text-light dark:text-text-dark mb-2 line-clamp-2 group-hover:text-primary transition-colors text-sm font-display">
                                            {note.title || 'Sin Título'}
                                        </h4>

                                        {note.feasibility_score > 0 && (
                                            <div className="flex items-center gap-2 mt-3">
                                                <div className="flex-1 h-1.5 bg-surface-light dark:bg-surface-dark rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${note.feasibility_score > 70 ? 'bg-emerald-500' :
                                                            note.feasibility_score > 40 ? 'bg-amber-500' : 'bg-red-500'
                                                            }`}
                                                        style={{ width: `${note.feasibility_score}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs font-mono text-text-secondary-light dark:text-text-secondary-dark">{note.feasibility_score}%</span>
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
