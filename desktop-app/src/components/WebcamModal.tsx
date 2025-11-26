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
            setError(err.response?.data?.detail || "Error al capturar imagen. Asegúrate de que la cámara no esté en uso.");
        } finally {
            setCapturing(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 rounded-2xl overflow-hidden max-w-md w-full border border-gray-800 shadow-2xl">
                <div className="p-4 flex justify-between items-center border-b border-gray-800">
                    <h3 className="text-lg font-semibold text-white">Capturar desde Backend</h3>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="relative bg-black aspect-video flex items-center justify-center overflow-hidden">
                    <img
                        src="http://localhost:8001/api/video_feed"
                        alt="Webcam Preview"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            setError("No se pudo cargar la vista previa. Verifica que la cámara no esté en uso.");
                        }}
                    />
                </div>

                <div className="p-6 flex flex-col items-center justify-center gap-4 bg-gray-900">
                    {error && (
                        <div className="text-red-400 text-sm text-center bg-red-900/20 p-3 rounded-lg w-full">
                            {error}
                        </div>
                    )}
                    <button
                        onClick={handleCapture}
                        disabled={capturing}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 text-white px-8 py-3 rounded-full flex items-center gap-2 font-medium transition-all transform hover:scale-105 w-full justify-center"
                    >
                        {capturing ? (
                            <>
                                <RefreshCw className="w-5 h-5 animate-spin" />
                                Capturando...
                            </>
                        ) : (
                            <>
                                <Camera className="w-5 h-5" />
                                Tomar Foto
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default WebcamModal;
