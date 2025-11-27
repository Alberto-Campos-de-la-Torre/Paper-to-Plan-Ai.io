import React, { useState } from 'react';
import { LayoutDashboard, Kanban, Settings, Camera, LogOut, Upload, CheckCircle2, QrCode, Wifi, X } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';

interface SidebarProps {
    onUpload: () => void;
    onWebcam: () => void;
    // Filter Props
    activeFilter: string;
    onFilterChange: (filter: string) => void;
    showCompleted: boolean;
    onToggleCompleted: () => void;
    // Server Props
    serverStatus: boolean;
    onToggleServer: () => void;
    // User Props
    users: string[];
    currentUser: string;
    onUserChange: (user: string) => void;
    onAddUser: () => void;
    onLogout: () => void;
    onShowUsers: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
    onUpload,
    onWebcam,
    activeFilter,
    onFilterChange,
    showCompleted,
    onToggleCompleted,
    serverStatus,
    onToggleServer,
    currentUser,
    onLogout,
    onShowUsers
}) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [showQRModal, setShowQRModal] = useState(false);

    const isActive = (path: string) => location.pathname === path;

    const handleShowQR = () => {
        if (serverStatus) {
            setShowQRModal(true);
        }
    };

    const NavItem = ({ icon: Icon, label, path }: { icon: any, label: string, path: string }) => {
        const active = isActive(path);
        return (
            <button
                onClick={() => navigate(path)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded transition-all duration-200 group ${active
                    ? 'bg-cyan-500 text-black font-bold'
                    : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                    }`}
            >
                <Icon className={`w-4 h-4 ${active ? 'text-black' : 'text-gray-500 group-hover:text-gray-300'}`} />
                <span className="text-sm tracking-wide font-mono">{label}</span>
            </button>
        );
    };

    const FilterChip = ({ label, value }: { label: string, value: string }) => (
        <button
            onClick={() => onFilterChange(value)}
            className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider transition-all duration-200 border font-mono ${activeFilter === value
                ? 'bg-cyan-500 text-black border-cyan-500'
                : 'bg-transparent text-gray-400 border-gray-600 hover:border-gray-400 hover:text-gray-300'
                }`}
        >
            {label}
        </button>
    );

    return (
        <>
            <aside className="w-64 h-full bg-black/80 backdrop-blur-xl border-r border-gray-800 flex flex-col shrink-0 relative z-20 overflow-hidden font-mono">
                {/* Logo Area */}
                <div className="p-6 border-b border-gray-800">
                    <h1 className="text-2xl font-bold text-white tracking-tight font-display">PaperToPlan</h1>
                    <p className="text-xs text-gray-500 mt-1 tracking-widest uppercase">AI WORKSPACE</p>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar px-4 py-6 space-y-8">
                    {/* Primary Actions */}
                    <div className="space-y-3">
                        <button
                            onClick={onUpload}
                            className="w-full bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 p-3 rounded flex items-center gap-3 font-bold transition-all duration-300 group"
                        >
                            <Upload className="w-5 h-5 group-hover:scale-110 transition-transform" />
                            <span className="tracking-wide text-sm">SUBIR NOTA</span>
                        </button>
                        <button
                            onClick={onWebcam}
                            className="w-full bg-gray-800/50 hover:bg-gray-800 text-gray-300 border border-gray-700 p-3 rounded flex items-center gap-3 font-medium transition-all duration-300"
                        >
                            <Camera className="w-5 h-5 text-gray-400" />
                            <span className="tracking-wide text-sm">USAR CÁMARA</span>
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="space-y-1">
                        <div className="px-2 text-xs font-bold text-gray-500 uppercase tracking-widest mb-3">Menu</div>
                        <NavItem icon={LayoutDashboard} label="Dashboard" path="/" />
                        <NavItem icon={Kanban} label="Kanban Board" path="/kanban" />
                        <NavItem icon={Settings} label="Configuración" path="/settings" />
                    </nav>

                    {/* Filters Section */}
                    <div className="space-y-3">
                        <div className="px-2 text-xs font-bold text-gray-500 uppercase tracking-widest mb-2">
                            Filtros
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <FilterChip label="TODO" value="all" />
                            <FilterChip label="CORTO" value="Corto Plazo" />
                            <FilterChip label="MEDIO" value="Mediano Plazo" />
                            <FilterChip label="LARGO" value="Largo Plazo" />
                        </div>

                        <div className="mt-4 px-1">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <div className={`w-4 h-4 border rounded flex items-center justify-center transition-colors ${showCompleted ? 'bg-cyan-500 border-cyan-500' : 'border-gray-600 group-hover:border-gray-400'}`}>
                                    {showCompleted && <CheckCircle2 className="w-3 h-3 text-black" />}
                                </div>
                                <span className="text-sm text-gray-400 group-hover:text-gray-300 select-none">Mostrar Completados</span>
                                <input type="checkbox" className="hidden" checked={showCompleted} onChange={onToggleCompleted} />
                            </label>
                        </div>
                    </div>
                </div>

                {/* User Profile */}
                <div className="p-4 border-t border-gray-800 bg-black/40">
                    <div className="flex items-center justify-between p-2 rounded hover:bg-white/5 cursor-pointer transition-colors group">
                        <div className="flex items-center gap-3" onClick={onShowUsers}>
                            <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center text-black font-bold font-display">
                                {currentUser.charAt(0)}
                            </div>
                            <div>
                                <p className="font-bold text-base text-gray-200 group-hover:text-white transition-colors">{currentUser}</p>
                                <p className="text-xs text-gray-500 uppercase tracking-wider">Pro Plan</p>
                            </div>
                        </div>
                        <button onClick={onLogout} className="text-gray-500 hover:text-red-400 transition-colors p-1">
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Mobile App Connection Status */}
                    <div className="mt-4 px-2 flex items-center justify-between bg-white/5 p-3 rounded-lg">
                        <div className="flex items-center gap-3">
                            <button
                                onClick={onToggleServer}
                                className={`w-8 h-4 rounded-full transition-colors relative ${serverStatus ? 'bg-green-500' : 'bg-gray-600'}`}
                            >
                                <div className={`absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform ${serverStatus ? 'translate-x-4' : 'translate-x-0'}`} />
                            </button>
                            <span className="text-xs text-gray-300 font-mono uppercase">Mobile App</span>
                        </div>
                        <button
                            onClick={handleShowQR}
                            disabled={!serverStatus}
                            className={`text-gray-400 hover:text-white transition-colors ${!serverStatus && 'opacity-30 cursor-not-allowed'}`}
                            title="Mostrar código QR"
                        >
                            <QrCode className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* QR Modal */}
            {showQRModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in" onClick={() => setShowQRModal(false)}>
                    <div className="bg-[#0f172a] border border-white/10 rounded-2xl p-8 shadow-2xl max-w-sm w-full relative text-center" onClick={e => e.stopPropagation()}>
                        <button
                            onClick={() => setShowQRModal(false)}
                            className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        <h3 className="text-xl font-bold text-white mb-2 font-display">Conectar Móvil</h3>
                        <p className="text-gray-400 text-sm mb-6">Escanea este código con tu dispositivo</p>

                        <div className="bg-white p-4 rounded-xl inline-block mb-6">
                            <QRCodeSVG value={`http://${window.location.hostname}:8001`} size={200} />
                        </div>

                        <div className="flex items-center justify-center gap-2 text-xs text-gray-500 font-mono bg-white/5 p-3 rounded-lg">
                            <Wifi className="w-3 h-3" />
                            <span>Asegúrate de estar en la misma red Wi-Fi</span>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Sidebar;
