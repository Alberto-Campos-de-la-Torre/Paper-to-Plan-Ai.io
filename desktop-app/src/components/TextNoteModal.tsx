import React, { useState } from 'react';
import { X, Send, FileText } from 'lucide-react';

interface TextNoteModalProps {
    onClose: () => void;
    onSubmit: (text: string) => Promise<void>;
}

const TextNoteModal: React.FC<TextNoteModalProps> = ({ onClose, onSubmit }) => {
    const [text, setText] = useState('');
    const [sending, setSending] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!text.trim()) return;

        try {
            setSending(true);
            await onSubmit(text);
            onClose();
        } catch (error) {
            console.error("Error sending text note:", error);
            alert("Error al enviar la nota.");
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in" onClick={onClose}>
            <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-2xl p-8 shadow-2xl max-w-2xl w-full relative" onClick={e => e.stopPropagation()}>
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="flex items-center gap-3 mb-6 border-b border-border-light dark:border-border-dark pb-4">
                    <FileText className="w-6 h-6 text-primary" />
                    <h3 className="text-xl font-bold text-text-light dark:text-text-dark font-display">Nueva Nota de Texto</h3>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-2">
                            Contenido de la Nota
                        </label>
                        <textarea
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            className="w-full h-64 bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded-lg p-4 text-text-light dark:text-text-dark focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all resize-none font-mono leading-relaxed"
                            placeholder="Escribe tu idea, requerimiento o plan aquí..."
                            required
                            autoFocus
                        />
                    </div>

                    <div className="flex justify-end pt-2">
                        <button
                            type="submit"
                            disabled={sending || !text.trim()}
                            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-bold transition-all ${sending || !text.trim()
                                    ? 'bg-gray-300 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
                                    : 'bg-primary hover:bg-primary/90 text-surface-dark shadow-lg hover:shadow-primary/20'
                                }`}
                        >
                            <Send className={`w-4 h-4 ${sending ? 'animate-pulse' : ''}`} />
                            {sending ? 'Procesando...' : 'Procesar con IA'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TextNoteModal;
