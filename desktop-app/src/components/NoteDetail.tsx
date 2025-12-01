import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getNoteDetail, Note, deleteNote, regenerateNote, markCompleted } from '../api/client';
import { ArrowLeft, CheckCircle, Clock, FileText, Code, Settings, Edit3, Trash2, RefreshCw, CheckSquare, Download } from 'lucide-react';
import { save } from '@tauri-apps/plugin-dialog';
import { writeTextFile } from '@tauri-apps/plugin-fs';

const NoteDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [note, setNote] = useState<Note | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [editableText, setEditableText] = useState('');
    const [regenerating, setRegenerating] = useState(false);

    useEffect(() => {
        if (id) {
            fetchNote();
        }
    }, [id]);

    const fetchNote = () => {
        setLoading(true);
        getNoteDetail(parseInt(id!, 10))
            .then(note => {
                setNote(note);
                setEditableText(note.raw_text || '');
            })
            .catch(() => setError('Failed to fetch note details.'))
            .finally(() => setLoading(false));
    };

    const handleDelete = async () => {
        if (note) {
            if (window.confirm('¿Estás seguro de que quieres eliminar esta nota?')) {
                await deleteNote(note.id);
                navigate('/');
            }
        }
    };

    const handleRegenerate = async () => {
        if (note) {
            try {
                setRegenerating(true);
                await regenerateNote(note.id, editableText);
                alert('Nota enviada para regeneración. El proceso puede tardar unos momentos.');
                navigate('/'); // Go back to dashboard to see progress
            } catch (error) {
                console.error("Error regenerating note:", error);
                alert('Error al regenerar la nota.');
            } finally {
                setRegenerating(false);
            }
        }
    };

    const handleMarkCompleted = async () => {
        if (note) {
            await markCompleted(note.id);
            fetchNote();
        }
    };

    const handleExportMarkdown = async () => {
        if (!note) return;

        const markdownContent = `
# ${note.title || 'Sin Título'}

**Viabilidad:** ${note.feasibility_score || 0}/100
**Tiempo Estimado:** ${note.implementation_time || 'Desconocido'}

## Resumen Ejecutivo
${note.summary || 'No disponible'}

## Stack Recomendado
${note.recommended_stack?.map(tech => `- ${tech}`).join('\n') || 'No especificado'}

## Consideraciones Técnicas
${note.technical_considerations?.map(item => `- ${item}`).join('\n') || 'No especificadas'}

## Texto Original
${note.raw_text || ''}
        `.trim();

        try {
            // Try Tauri Save Dialog
            const filePath = await save({
                filters: [{
                    name: 'Markdown',
                    extensions: ['md']
                }],
                defaultPath: `${(note.title || 'nota').replace(/\s+/g, '_').toLowerCase()}.md`
            });

            if (filePath) {
                await writeTextFile(filePath, markdownContent);
                alert('Nota exportada correctamente.');
            }
        } catch (error) {
            console.error("Tauri export failed, falling back to browser download:", error);
            try {
                const blob = new Blob([markdownContent], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${(note.title || 'nota').replace(/\s+/g, '_').toLowerCase()}.md`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (fallbackError) {
                console.error("Browser export failed:", fallbackError);
                alert("Error al exportar el archivo Markdown.");
            }
        }
    };

    if (loading) {
        return <div className="flex items-center justify-center h-screen bg-background-dark text-text-dark">Cargando...</div>;
    }

    if (error || !note) {
        return <div className="flex items-center justify-center h-screen bg-background-dark text-red-500">{error || 'Nota no encontrada.'}</div>;
    }

    return (
        <div className="p-4 sm:p-6 md:p-8 bg-background-light dark:bg-background-dark font-display text-gray-900 dark:text-gray-300 h-screen flex flex-col overflow-hidden transition-colors duration-300">
            <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 flex-shrink-0">
                <button onClick={() => navigate('/')} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                    <ArrowLeft className="w-4 h-4" />
                    Volver al Dashboard
                </button>
                <div className={`flex items-center gap-2 text-sm ${note.status === 'completed' ? 'text-green-600 dark:text-green-400' : 'text-cyan-600 dark:text-cyan-400'}`}>
                    <CheckCircle className="w-4 h-4" />
                    <span>{note.status === 'completed' ? 'Proyecto Completado' : 'Análisis Completado'}</span>
                </div>
            </header>
            <main className="space-y-6 flex-1 overflow-y-auto custom-scrollbar pr-2">
                <section className="border border-border-light dark:border-border-dark p-6 bg-surface-light dark:bg-surface-dark rounded-lg shadow-sm">
                    <h1 className="text-2xl sm:text-3xl font-bold text-text-light dark:text-text-dark mb-3 font-display">
                        {note.title}
                    </h1>
                    <div className="flex items-center gap-2 text-sm text-text-secondary-light dark:text-text-secondary-dark font-mono">
                        <Clock className="w-4 h-4" />
                        <span>Viabilidad: {note.feasibility_score}/100</span>
                        <span className="inline-block w-1.5 h-1.5 bg-text-secondary-light dark:bg-text-secondary-dark rounded-full mx-1"></span>
                        <span>{note.implementation_time}</span>
                    </div>
                </section>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-6">
                        <section className="border border-border-light dark:border-border-dark rounded-lg overflow-hidden bg-surface-light dark:bg-surface-dark shadow-sm">
                            <h2 className="flex items-center gap-3 font-bold text-lg bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark p-4 border-b border-border-light dark:border-border-dark font-display">
                                <FileText className="w-5 h-5 text-primary" />
                                Resumen Ejecutivo
                            </h2>
                            <p className="p-4 leading-relaxed text-text-light dark:text-text-dark font-body">
                                {note.summary}
                            </p>
                        </section>
                        <section className="border border-border-light dark:border-border-dark rounded-lg overflow-hidden bg-surface-light dark:bg-surface-dark shadow-sm">
                            <h2 className="flex items-center gap-3 font-bold text-lg bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark p-4 border-b border-border-light dark:border-border-dark font-display">
                                <Code className="w-5 h-5 text-primary" />
                                Stack Recomendado
                            </h2>
                            <div className="p-4 flex flex-wrap gap-2">
                                {note.recommended_stack?.map((tech, index) => (
                                    <span key={index} className="px-3 py-1 bg-primary/10 text-primary border border-primary/20 rounded-full text-sm font-mono">
                                        {tech}
                                    </span>
                                ))}
                            </div>
                        </section>
                    </div>
                    <section className="border border-border-light dark:border-border-dark rounded-lg overflow-hidden bg-surface-light dark:bg-surface-dark shadow-sm">
                        <h2 className="flex items-center gap-3 font-bold text-lg bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark p-4 border-b border-border-light dark:border-border-dark font-display">
                            <Settings className="w-5 h-5 text-primary" />
                            Consideraciones Técnicas
                        </h2>
                        <ul className="p-4 sm:p-6 space-y-3 list-disc list-inside text-text-light dark:text-text-dark font-body">
                            {note.technical_considerations?.map((item, index) => item.trim() && <li key={index} className="pl-2">{item.trim()}</li>)}
                        </ul>
                    </section>
                </div>
                <section className="border border-border-light dark:border-border-dark rounded-lg overflow-hidden bg-surface-light dark:bg-surface-dark shadow-sm">
                    <h2 className="flex items-center gap-3 font-bold text-lg bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark p-4 border-b border-border-light dark:border-border-dark font-display">
                        <Edit3 className="w-5 h-5 text-primary" />
                        Texto Extraído (Editable):
                    </h2>
                    <div className="p-4">
                        <textarea
                            className="w-full bg-transparent border border-border-light dark:border-border-dark rounded p-2 text-sm leading-relaxed text-text-light dark:text-text-dark focus:border-primary outline-none font-mono"
                            value={editableText}
                            onChange={(e) => setEditableText(e.target.value)}
                            rows={6}
                        />
                    </div>
                </section>

                <footer className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-300 dark:border-gray-700 pb-6">
                    <div className="flex flex-wrap items-center gap-2">
                        <button onClick={handleDelete} className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-red-900/20 hover:text-red-400 hover:border-red-900/50 transition-colors">
                            <Trash2 className="w-4 h-4" />
                            Eliminar Nota
                        </button>
                        <button
                            onClick={handleRegenerate}
                            disabled={regenerating || note.status === 'completed'}
                            className={`flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-cyan-900/20 hover:text-cyan-400 hover:border-cyan-900/50 transition-colors ${regenerating || note.status === 'completed' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                            <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
                            {regenerating ? 'Regenerando...' : 'Regenerar Plan'}
                        </button>
                        <button
                            onClick={handleMarkCompleted}
                            disabled={note.status === 'completed'}
                            className={`flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-green-900/20 hover:text-green-400 hover:border-green-900/50 transition-colors ${note.status === 'completed' ? 'opacity-50 cursor-not-allowed bg-green-900/10 text-green-500 border-green-900/30' : ''}`}
                        >
                            <CheckSquare className="w-4 h-4" />
                            {note.status === 'completed' ? 'Completado' : 'Marcar Completado'}
                        </button>
                    </div>
                    <button
                        onClick={handleExportMarkdown}
                        className="flex items-center gap-2 text-sm px-3 py-2 border border-gray-300 dark:border-gray-600 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors w-full sm:w-auto"
                    >
                        <Download className="w-4 h-4" />
                        Exportar MD
                    </button>
                </footer>
            </main>
        </div>
    );
};

export default NoteDetail;
