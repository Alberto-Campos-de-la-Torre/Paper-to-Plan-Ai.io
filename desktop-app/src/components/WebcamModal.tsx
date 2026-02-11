import React, { useState } from 'react';
import { X, Camera, RefreshCw } from 'lucide-react';
import { captureWebcam } from '../api/client';

interface WebcamModalProps {
    onClose: () => void;
    onCaptureComplete: () => void;
}

const WebcamModal: React.FC<WebcamModalProps> = ({ onClose, onCaptureComplete }) => {
    const [error, setError] = useState<string | null>(null);
    const [capturing, setCapturing] = useState(false);

    const handleCapture = async () => {
        try {
            setCapturing(true);
            setError(null);
            await captureWebcam();
            onCaptureComplete();
            onClose();
        } catch (err: any) {
            console.error("Capture failed:", err);
            setError(err.response?.data?.detail || "Error al capturar imagen. Asegurate de que la camara no este en uso.");
        } finally {
            setCapturing(false);
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content overflow-hidden" style={{ maxWidth: '480px' }}>
                <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                    <h3 className="text-lg font-semibold">Captura de Documento</h3>
                    <button onClick={onClose} style={{ color: 'var(--color-text-muted)' }}>
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="relative aspect-video flex items-center justify-center overflow-hidden" style={{ background: 'var(--color-surface-alt)' }}>
                    <img
                        src="http://localhost:8001/api/video_feed"
                        alt="Vista previa"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            setError("No se pudo cargar la vista previa. Verifica que la camara no este en uso.");
                        }}
                    />
                </div>

                <div className="p-6 flex flex-col items-center gap-4">
                    {error && (
                        <div className="text-sm text-center p-3 rounded-lg w-full tag-status-error">
                            {error}
                        </div>
                    )}
                    <button
                        onClick={handleCapture}
                        disabled={capturing}
                        className="btn btn-primary w-full py-3"
                    >
                        {capturing ? (
                            <>
                                <RefreshCw className="w-5 h-5 animate-spin" />
                                Capturando...
                            </>
                        ) : (
                            <>
                                <Camera className="w-5 h-5" />
                                Capturar Documento
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default WebcamModal;
