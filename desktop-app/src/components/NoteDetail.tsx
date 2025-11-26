import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getNoteDetail, deleteNote, regenerateNote, markCompleted, Note } from '../api/client';
import { ArrowLeft, FileText, Trash2, RefreshCw, CheckCircle, Download, Clock, Zap, Code, AlertTriangle, Edit3 } from 'lucide-react';

const NoteDetail: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [note, setNote] = useState<Note | null>(null);
    const [loading, setLoading] = useState(true);
    const [rawText, setRawText] = useState('');
    const [isRegenerating, setIsRegenerating] = useState(false);

    useEffect(() => {
        if (id) {
            loadNote(parseInt(id));
        }
    }, [id]);

    const loadNote = async (noteId: number) => {
        try {
            const data = await getNoteDetail(noteId);
            setNote(data);
            setRawText(data.raw_text || '');
        } catch (error) {
            console.error("Error loading note:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!note || !window.confirm('¿Estás seguro de que quieres eliminar esta nota?')) return;

        try {
            await deleteNote(note.id);
            navigate('/');
        } catch (error) {
            console.error("Error deleting note:", error);
            alert('Error al eliminar la nota');
        }
    };

    const handleRegenerate = async () => {
        if (!note) return;

        setIsRegenerating(true);
        try {
            await regenerateNote(note.id, rawText);
            await loadNote(note.id);
        } catch (error) {
            console.error("Error regenerating note:", error);
            alert('Error al regenerar el plan');
        } finally {
            setIsRegenerating(false);
        }
    };

    const handleMarkCompleted = async () => {
        if (!note) return;

        try {
            await markCompleted(note.id);
            await loadNote(note.id);
        } catch (error) {
            console.error("Error marking as completed:", error);
            alert('Error al marcar como completado');
        }
    };

    const handleExportMD = () => {
        if (!note) return;

        let content = `# ${note.title || 'Sin Título'}\n\n`;
        content += `**Feasibility Score:** ${note.feasibility_score}/100\n`;
        content += `**Implementation Time:** ${note.implementation_time}\n\n`;

        if (note.summary) {
            content += `## Summary\n${note.summary}\n\n`;
        }

        if (note.recommended_stack && note.recommended_stack.length > 0) {
            content += `## Recommended Stack\n`;
            note.recommended_stack.forEach(item => {
                content += `- ${item}\n`;
            });
            content += '\n';
        }

        if (note.technical_considerations && note.technical_considerations.length > 0) {
            content += `## Technical Considerations\n`;
            note.technical_considerations.forEach(item => {
                content += `- ${item}\n`;
            });
        }

        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${note.title || 'nota'}.md`;
        a.click();
        URL.revokeObjectURL(url);
    };

    if (loading) return (
        <div className="flex justify-center items-center h-full bg-black">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
        </div>
    );

    if (!note) return <div className="text-white p-8">Nota no encontrada</div>;

    return (
        <div className="h-full overflow-y-auto bg-black font-mono text-gray-300">
            <div className="p-4 sm:p-6 md:p-8 max-w-7xl mx-auto space-y-6">
                <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                    <button
                        onClick={() => navigate('/')}
                        className="flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        VOLVER AL DASHBOARD
                    </button>

                    <div className="flex items-center gap-2 text-sm text-green-400 font-bold">
                        <CheckCircle className="w-4 h-4" />
                        <span>ANÁLISIS COMPLETADO</span>
                    </div>
                </header>

                {/* Main Title Section */}
                <section className="border border-gray-800 bg-[#0c0d17] p-6 rounded-lg">
                    <h1 className="text-2xl sm:text-3xl font-bold text-white mb-4 font-display tracking-wide leading-tight">
                        {note.title || 'Sin Título'}
                    </h1>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 font-mono">
                        <div className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            <span>VIABILIDAD: <span className="text-white font-bold">{note.feasibility_score}/100</span></span>
                        </div>
                        <span className="w-1 h-1 bg-gray-700 rounded-full"></span>
                        <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-cyan-400" />
                            <span className="uppercase">{note.implementation_time}</span>
                        </div>
                    </div>
                </section>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-6">
                        {/* Summary Section */}
                        <section className="border border-gray-800 bg-[#0c0d17] rounded-lg overflow-hidden">
                            <h2 className="flex items-center gap-3 font-bold text-sm bg-[#1a1b26] text-white p-4 border-b border-gray-800 font-display tracking-wider">
                                <FileText className="w-4 h-4 text-cyan-400" />
                                RESUMEN EJECUTIVO
                            </h2>
                            <p className="p-6 leading-relaxed text-sm">
                                {note.summary || 'No hay resumen disponible.'}
                            </p>
                        </section>

                        {/* Tech Stack Section */}
                        <section className="border border-gray-800 bg-[#0c0d17] rounded-lg overflow-hidden">
                            <h2 className="flex items-center gap-3 font-bold text-sm bg-[#1a1b26] text-white p-4 border-b border-gray-800 font-display tracking-wider">
                                <Code className="w-4 h-4 text-purple-400" />
                                STACK RECOMENDADO
                            </h2>
                            <p className="p-6 leading-relaxed text-sm font-mono text-cyan-300/80">
                                {note.recommended_stack && note.recommended_stack.length > 0 ? (
                                    note.recommended_stack.join(' | ')
                                ) : 'No especificado'}
                            </p>
                        </section>
                    </div>

                    {/* Technical Considerations */}
                    <section className="border border-gray-800 bg-[#0c0d17] rounded-lg overflow-hidden h-full">
                        <h2 className="flex items-center gap-3 font-bold text-sm bg-[#1a1b26] text-white p-4 border-b border-gray-800 font-display tracking-wider">
                            <AlertTriangle className="w-4 h-4 text-orange-400" />
                            CONSIDERACIONES TÉCNICAS
                        </h2>
                        <ul className="p-6 space-y-3 list-disc list-inside text-sm text-gray-400">
                            {note.technical_considerations && note.technical_considerations.length > 0 ? (
                                note.technical_considerations.map((item, index) => (
                                    <li key={index} className="leading-relaxed">{item}</li>
                                ))
                            ) : (
                                <li>No hay consideraciones técnicas especificadas.</li>
                            )}
                        </ul>
                    </section>
                </div>

                {/* Raw Text Section */}
                <section className="border border-gray-800 bg-[#0c0d17] rounded-lg overflow-hidden">
                    <h2 className="flex items-center gap-3 font-bold text-sm bg-[#1a1b26] text-white p-4 border-b border-gray-800 font-display tracking-wider">
                        <Edit3 className="w-4 h-4 text-gray-400" />
                        TEXTO EXTRAÍDO (EDITABLE)
                    </h2>
                    <div className="p-4">
                        <textarea
                            value={rawText}
                            onChange={(e) => setRawText(e.target.value)}
                            className="w-full bg-transparent border-none focus:ring-0 p-0 text-sm leading-relaxed text-gray-100 font-mono resize-y min-h-[100px]"
                            placeholder="Texto extraído..."
                        />
                    </div>
                </section>

                {/* Footer Actions */}
                <footer className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-800">
                    <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                        <button
                            onClick={handleDelete}
                            className="flex items-center gap-2 text-xs px-4 py-2 border border-gray-800 bg-[#1a1b26] hover:bg-red-900/20 hover:border-red-800 hover:text-red-400 transition-colors rounded"
                        >
                            <Trash2 className="w-3 h-3" />
                            ELIMINAR NOTA
                        </button>
                        <button
                            onClick={handleRegenerate}
                            disabled={isRegenerating}
                            className="flex items-center gap-2 text-xs px-4 py-2 border border-gray-800 bg-[#1a1b26] hover:bg-cyan-900/20 hover:border-cyan-800 hover:text-cyan-400 transition-colors rounded disabled:opacity-50"
                        >
                            <RefreshCw className={`w-3 h-3 ${isRegenerating ? 'animate-spin' : ''}`} />
                            {isRegenerating ? 'REGENERANDO...' : 'REGENERAR PLAN'}
                        </button>
                        <button
                            onClick={handleMarkCompleted}
                            className="flex items-center gap-2 text-xs px-4 py-2 border border-gray-800 bg-[#1a1b26] hover:bg-green-900/20 hover:border-green-800 hover:text-green-400 transition-colors rounded"
                        >
                            <CheckCircle className="w-3 h-3" />
                            MARCAR COMPLETADO
                        </button>
                    </div>

                    <button
                        onClick={handleExportMD}
                        className="flex items-center justify-center gap-2 text-xs px-4 py-2 border border-gray-800 bg-[#1a1b26] hover:bg-white/10 hover:text-white transition-colors rounded w-full sm:w-auto font-bold"
                    >
                        <Download className="w-3 h-3" />
                        EXPORTAR MD
                    </button>
                </footer>
            </div>
        </div>
    );
};

export default NoteDetail;
