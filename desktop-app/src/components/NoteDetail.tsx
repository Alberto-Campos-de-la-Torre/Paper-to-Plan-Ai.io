import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getNoteDetail, Note, deleteNote, regenerateNote, markCompleted } from '../api/client';

const NoteDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [note, setNote] = useState<Note | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [editableText, setEditableText] = useState('');

    useEffect(() => {
        if (id) {
            getNoteDetail(parseInt(id, 10))
                .then(note => {
                    setNote(note);
                    setEditableText(note.raw_text || '');
                })
                .catch(() => setError('Failed to fetch note details.'))
                .finally(() => setLoading(false));
        }
    }, [id]);

    const handleDelete = async () => {
        if (note) {
            await deleteNote(note.id);
            navigate('/');
        }
    };

    const handleRegenerate = async () => {
        if (note) {
            await regenerateNote(note.id, editableText);
            // Optionally, refresh the note details
            if (id) {
                setLoading(true);
                getNoteDetail(parseInt(id, 10))
                    .then(note => {
                        setNote(note);
                        setEditableText(note.raw_text || '');
                    })
                    .catch(() => setError('Failed to fetch note details.'))
                    .finally(() => setLoading(false));
            }
        }
    };

    const handleMarkCompleted = async () => {
        if (note) {
            await markCompleted(note.id);
            // Optionally, refresh the note details
            if (id) {
                setLoading(true);
                getNoteDetail(parseInt(id, 10))
                    .then(note => {
                        setNote(note);
                        setEditableText(note.raw_text || '');
                    })
                    .catch(() => setError('Failed to fetch note details.'))
                    .finally(() => setLoading(false));
            }
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center h-screen bg-background-dark text-text-dark">Loading...</div>;
    }

    if (error || !note) {
        return <div className="flex items-center justify-center h-screen bg-background-dark text-red-500">{error || 'Note not found.'}</div>;
    }

    return (
        <div className="p-4 sm:p-6 md:p-8 bg-background-light dark:bg-background-dark font-display text-gray-900 dark:text-gray-300 min-h-screen">
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                    <span className="material-icons text-base">arrow_back</span>
                    Volver al Dashboard
                </button>
                <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                    <span className="material-icons text-base">check_circle</span>
                    <span>Análisis Completado</span>
                </div>
            </header>
            <main className="space-y-6">
                <section className="border border-gray-300 dark:border-gray-700 p-6">
                    <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mb-3">
                        {note.title}
                    </h1>
                    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                        <span className="material-icons text-lg">schedule</span>
                        <span>Viabilidad: {note.feasibility_score}/100</span>
                        <span className="inline-block w-1.5 h-1.5 bg-gray-400 dark:bg-gray-600 rounded-full mx-1"></span>
                        <span>{note.implementation_time}</span>
                    </div>
                </section>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-6">
                        <section className="border border-gray-300 dark:border-gray-700">
                            <h2 className="flex items-center gap-3 font-bold text-lg bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white p-4 border-b border-gray-300 dark:border-gray-700">
                                <span className="material-icons">description</span>
                                Resumen Ejecutivo
                            </h2>
                            <p className="p-4 leading-relaxed">
                                {note.summary}
                            </p>
                        </section>
                        <section className="border border-gray-300 dark:border-gray-700">
                            <h2 className="flex items-center gap-3 font-bold text-lg bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white p-4 border-b border-gray-300 dark:border-gray-700">
                                <span className="material-icons">code</span>
                                Stack Recomendado
                            </h2>
                            <p className="p-4 leading-relaxed">
                                {note.recommended_stack?.join(', ')}
                            </p>
                        </section>
                    </div>
                    <section className="border border-gray-300 dark:border-gray-700">
                        <h2 className="flex items-center gap-3 font-bold text-lg bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white p-4 border-b border-gray-300 dark:border-gray-700">
                            <span className="material-icons">engineering</span>
                            Consideraciones Técnicas
                        </h2>
                        <ul className="p-4 sm:p-6 space-y-3 list-disc list-inside">
                            {note.technical_considerations?.map((item, index) => item.trim() && <li key={index}>{item.trim()}</li>)}
                        </ul>
                    </section>
                </div>
                <section className="border border-gray-300 dark:border-gray-700">
                    <h2 className="flex items-center gap-3 font-bold text-lg bg-gray-200 dark:bg-gray-800 text-gray-900 dark:text-white p-4 border-b border-gray-300 dark:border-gray-700">
                        <span className="material-icons">edit_note</span>
                        Texto Extraído (Editable):
                    </h2>
                    <div className="p-4">
                        <textarea
                            className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm leading-relaxed text-gray-700 dark:text-gray-400"
                            value={editableText}
                            onChange={(e) => setEditableText(e.target.value)}
                            rows={2}
                        />
                    </div>
                </section>
                <footer className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-300 dark:border-gray-700">
                    <div className="flex flex-wrap items-center gap-2">
                        <button onClick={handleDelete} className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                            <span className="material-icons text-base">delete_outline</span>
                            Eliminar Nota
                        </button>
                        <button onClick={handleRegenerate} className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                            <span className="material-icons text-base">refresh</span>
                            Regenerar Plan
                        </button>
                        <button onClick={handleMarkCompleted} className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                            <span className="material-icons text-base">check_box_outline_blank</span>
                            Marcar Completado
                        </button>
                    </div>
                    <button className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors w-full sm:w-auto">
                        <span className="material-icons text-base">download</span>
                        Exportar MD
                    </button>
                </footer>
            </main>
        </div>
    );
};

export default NoteDetail;
