import React, { useState, useRef } from 'react';
import { X, Camera, RefreshCw, AlertCircle } from 'lucide-react';
import { uploadImage } from '../api/client';

interface WebcamModalProps {
    onClose: () => void;
    onCaptureComplete: () => void;
}

const WebcamModal: React.FC<WebcamModalProps> = ({ onClose, onCaptureComplete }) => {
    const [error, setError] = useState<boolean>(false);
    const [capturing, setCapturing] = useState(false);
    const imgRef = useRef<HTMLImageElement>(null);

    const handleCapture = async () => {
        console.log("Starting capture process...");
        try {
            setCapturing(true);
            setError(false);

            // Capture from the image element (which is streaming from backend)
            if (!imgRef.current) {
                console.error("imgRef.current is null");
                throw new Error("No video stream available");
            }

            // Create a canvas to draw the image
            const canvas = document.createElement('canvas');
            canvas.width = imgRef.current.naturalWidth;
            canvas.height = imgRef.current.naturalHeight;

            const ctx = canvas.getContext('2d');
            if (!ctx) throw new Error("Could not get canvas context");

            // Draw the current frame
            try {
                ctx.drawImage(imgRef.current, 0, 0);
            } catch (drawError) {
                console.error("Error drawing image to canvas (likely CORS):", drawError);
                throw new Error("Security error: Cannot capture from video stream due to CORS. Ensure backend allows CORS.");
            }

            // Convert to blob
            const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg'));
            if (!blob) {
                throw new Error("Could not create image blob");
            }

            // Create file from blob
            const file = new File([blob], "webcam_capture.jpg", { type: "image/jpeg" });

            // Upload using existing uploadImage function
            console.log("Uploading image...");
            await uploadImage(file);
            console.log("Upload successful");

            onCaptureComplete();
            onClose();
        } catch (err: any) {
            console.error("Capture failed:", err);
            setError(true); // Changed to boolean
        } finally {
            setCapturing(false);
        }
    };

    const [retryCount, setRetryCount] = useState(0);
    const [streamUrl, setStreamUrl] = useState(`http://localhost:8001/api/video_feed?t=${Date.now()}`);

    const handleRetry = () => {
        setError(false);
        setRetryCount(prev => prev + 1);
        setStreamUrl(`http://localhost:8001/api/video_feed?t=${Date.now()}&retry=${retryCount + 1}`);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 backdrop-blur-sm animate-fade-in" onClick={onClose}>
            <div className="relative w-full max-w-4xl mx-4 bg-surface-light dark:bg-surface-dark rounded-2xl overflow-hidden shadow-2xl border border-border-light dark:border-border-dark" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="flex justify-between items-center p-4 border-b border-border-light dark:border-border-dark bg-background-light/50 dark:bg-background-dark/50 backdrop-blur-md">
                    <h3 className="text-xl font-bold text-text-light dark:text-text-dark font-display flex items-center gap-2">
                        <Camera className="w-5 h-5 text-primary" />
                        Captura de Cámara
                    </h3>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors text-text-light dark:text-text-dark">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Camera View */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden group">
                    {error ? (
                        <div className="text-center p-8">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                                <AlertCircle className="w-8 h-8 text-red-500" />
                            </div>
                            <p className="text-white text-lg font-medium mb-2">No se pudo conectar a la cámara</p>
                            <p className="text-gray-400 text-sm mb-6">Asegúrate de que el servidor backend esté corriendo y la cámara no esté en uso.</p>
                            <button
                                onClick={handleRetry}
                                className="px-6 py-2 bg-primary hover:bg-primary-dark text-white rounded-full transition-colors flex items-center gap-2 mx-auto"
                            >
                                <RefreshCw className="w-4 h-4" />
                                Reintentar Conexión
                            </button>
                        </div>
                    ) : (
                        <>
                            <img
                                ref={imgRef}
                                crossOrigin="anonymous"
                                src={streamUrl}
                                alt="Webcam Stream"
                                className="w-full h-full object-contain"
                                onError={(e) => {
                                    console.error("Webcam stream error:", e);
                                    setError(true);
                                }}
                                onLoad={() => {
                                    console.log("Webcam stream loaded successfully");
                                    // Only clear error if it was previously set, to avoid unnecessary re-renders
                                    if (error) setError(false);
                                }}
                            />
                            {/* Overlay Guidelines */}
                            <div className="absolute inset-0 border-2 border-white/10 pointer-events-none">
                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 border border-white/20 rounded-lg border-dashed"></div>
                            </div>
                        </>
                    )}
                </div>
                {/* The old error display div was removed as it's now handled by the conditional rendering above */}

                <div className="p-6 flex flex-col items-center justify-center gap-4 bg-surface-dark">
                    {error && (
                        <div className="text-red-400 text-sm text-center bg-red-900/20 p-3 rounded-lg w-full border border-red-900/50">
                            {error}
                        </div>
                    )}
                    <button
                        onClick={handleCapture}
                        disabled={capturing}
                        className="bg-primary hover:bg-primary/80 disabled:bg-gray-700 text-surface-dark px-8 py-3 rounded-full flex items-center gap-2 font-bold transition-all transform hover:scale-105 w-full justify-center font-display"
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
