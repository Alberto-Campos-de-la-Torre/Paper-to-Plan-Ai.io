import React, { useState, useRef } from 'react';
import { X, Camera, RefreshCw } from 'lucide-react';
import { uploadImage } from '../api/client';

interface WebcamModalProps {
    onClose: () => void;
    onCaptureComplete: () => void;
}

const WebcamModal: React.FC<WebcamModalProps> = ({ onClose, onCaptureComplete }) => {
    const [error, setError] = useState<string | null>(null);
    const [capturing, setCapturing] = useState(false);
    const imgRef = useRef<HTMLImageElement>(null);

    const handleCapture = async () => {
        console.log("Starting capture process...");
        try {
            setCapturing(true);
            setError(null);

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
            setError(err.message || err.response?.data?.detail || "Error al capturar imagen. Inténtalo de nuevo.");
        } finally {
            setCapturing(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm animate-fade-in">
            <div className="bg-surface-dark rounded-2xl overflow-hidden max-w-md w-full border border-border-dark shadow-2xl">
                <div className="p-4 flex justify-between items-center border-b border-border-dark">
                    <h3 className="text-lg font-semibold text-text-light font-display">Capturar desde Backend</h3>
                    <button onClick={onClose} className="text-text-secondary-dark hover:text-text-light transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="relative bg-black aspect-video flex items-center justify-center overflow-hidden">
                    <img
                        ref={imgRef}
                        crossOrigin="anonymous"
                        src={`http://localhost:8001/api/video_feed?t=${Date.now()}`}
                        alt="Webcam Preview"
                        className="w-full h-full object-cover"
                        onLoad={() => setError(null)}
                        onError={(e) => {
                            console.error("Image load error", e);
                            // Don't hide the image immediately, it might just be a frame drop
                            // e.currentTarget.style.display = 'none'; 
                            setError("Esperando señal de video...");
                        }}
                    />
                    {error && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/50 text-red-500 p-4 text-center backdrop-blur-sm">
                            <p>{error}</p>
                        </div>
                    )}
                </div>

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
