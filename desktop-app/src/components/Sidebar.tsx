import React, { useState } from 'react';
import { LayoutDashboard, Kanban, BarChart3, Camera, LogOut, Upload, CheckCircle2, QrCode, Wifi, X, Users, FileText, Sun, Moon } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';

interface SidebarProps {
    onUpload: () => void;
    onWebcam: () => void;
    onTextNote: () => void;
    activeFilter: string;
    onFilterChange: (filter: string) => void;
    showReviewed: boolean;
    onToggleReviewed: () => void;
    serverStatus: boolean;
    onToggleServer: () => void;
    currentUser: string;
    onLogout: () => void;
    onShowUsers: () => void;
    theme: 'light' | 'dark';
    onToggleTheme: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
    onUpload,
    onWebcam,
    onTextNote,
    activeFilter,
    onFilterChange,
    showReviewed,
    onToggleReviewed,
    serverStatus,
    onToggleServer,
    currentUser,
    onLogout,
    onShowUsers,
    theme,
    onToggleTheme
}) => {
    const navigate = useNavigate();
    const location = useLocation();
    const [showQRModal, setShowQRModal] = useState(false);

    const isActive = (path: string) => location.pathname === path;

    const NavItem = ({ icon: Icon, label, path }: { icon: any; label: string; path: string }) => {
        const active = isActive(path);
        return (
            <button
                onClick={() => navigate(path)}
                className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200"
                style={{
                    background: active ? 'var(--color-primary)' : 'transparent',
                    color: active ? '#ffffff' : 'var(--color-text-secondary)',
                }}
            >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{label}</span>
            </button>
        );
    };

    const FilterChip = ({ label, value }: { label: string; value: string }) => (
        <button
            onClick={() => onFilterChange(value)}
            className="px-2.5 py-1 rounded text-xs font-semibold transition-all duration-200"
            style={{
                background: activeFilter === value ? 'var(--color-primary)' : 'transparent',
                color: activeFilter === value ? '#ffffff' : 'var(--color-text-muted)',
                border: `1px solid ${activeFilter === value ? 'var(--color-primary)' : 'var(--color-border)'}`,
            }}
        >
            {label}
        </button>
    );

    return (
        <>
            <aside className="w-64 h-full flex flex-col shrink-0 relative z-20 overflow-hidden"
                   style={{ background: 'var(--color-surface)', borderRight: '1px solid var(--color-border-light)' }}>
                {/* Logo */}
                <div className="p-5" style={{ borderBottom: '1px solid var(--color-border-light)' }}>
                    <h1 className="text-xl font-bold font-display" style={{ color: 'var(--color-primary)' }}>
                        MEGI Records
                    </h1>
                    <p className="text-[10px] tracking-widest uppercase font-brand mt-0.5" style={{ color: 'var(--color-accent)' }}>
                        EXPEDIENTES MEDICOS
                    </p>
                </div>

                <div className="flex-1 overflow-y-auto px-4 py-5 space-y-6">
                    {/* Actions */}
                    <div className="space-y-2">
                        <button onClick={onUpload} className="btn btn-primary w-full justify-start">
                            <Upload className="w-4 h-4" />
                            <span className="text-sm">SUBIR DOCUMENTO</span>
                        </button>
                        <button onClick={onWebcam} className="btn btn-outline w-full justify-start">
                            <Camera className="w-4 h-4" />
                            <span className="text-sm">CAPTURAR DOCUMENTO</span>
                        </button>
                        <button onClick={onTextNote} className="btn btn-outline w-full justify-start">
                            <FileText className="w-4 h-4" />
                            <span className="text-sm">NUEVA CONSULTA</span>
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="space-y-1">
                        <div className="px-1 text-[10px] font-semibold uppercase tracking-widest mb-2" style={{ color: 'var(--color-text-muted)' }}>
                            Menu
                        </div>
                        <NavItem icon={LayoutDashboard} label="Expedientes" path="/" />
                        <NavItem icon={Users} label="Pacientes" path="/patients" />
                        <NavItem icon={Kanban} label="Tablero" path="/kanban" />
                        <NavItem icon={BarChart3} label="Estadisticas" path="/settings" />
                    </nav>

                    {/* Filters */}
                    <div className="space-y-3">
                        <div className="px-1 text-[10px] font-semibold uppercase tracking-widest" style={{ color: 'var(--color-text-muted)' }}>
                            Filtrar por tipo
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                            <FilterChip label="TODO" value="all" />
                            <FilterChip label="CONSULTAS" value="consultation" />
                            <FilterChip label="RECETAS" value="prescription" />
                            <FilterChip label="LABORATORIO" value="lab_result" />
                            <FilterChip label="REFERENCIAS" value="referral" />
                        </div>

                        <label className="flex items-center gap-3 cursor-pointer px-1 mt-3">
                            <div className="w-4 h-4 border rounded flex items-center justify-center transition-colors"
                                 style={{
                                     background: showReviewed ? 'var(--color-primary)' : 'transparent',
                                     borderColor: showReviewed ? 'var(--color-primary)' : 'var(--color-border)',
                                 }}>
                                {showReviewed && <CheckCircle2 className="w-3 h-3 text-white" />}
                            </div>
                            <span className="text-sm select-none" style={{ color: 'var(--color-text-secondary)' }}>
                                Mostrar Revisados
                            </span>
                            <input type="checkbox" className="hidden" checked={showReviewed} onChange={onToggleReviewed} />
                        </label>
                    </div>

                    {/* Theme toggle */}
                    <div className="px-1">
                        <button onClick={onToggleTheme} className="flex items-center gap-2 text-sm w-full px-3 py-2 rounded-lg transition-colors"
                                style={{ color: 'var(--color-text-secondary)' }}>
                            {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
                            <span>{theme === 'light' ? 'Modo Oscuro' : 'Modo Claro'}</span>
                        </button>
                    </div>
                </div>

                {/* User Profile */}
                <div className="p-4" style={{ borderTop: '1px solid var(--color-border-light)' }}>
                    <div className="flex items-center justify-between p-2 rounded-lg cursor-pointer transition-colors">
                        <div className="flex items-center gap-3" onClick={onShowUsers}>
                            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                                 style={{ background: 'var(--color-primary)' }}>
                                {currentUser.charAt(0)}
                            </div>
                            <div>
                                <p className="font-medium text-sm">{currentUser}</p>
                                <p className="text-[10px] uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Medico</p>
                            </div>
                        </div>
                        <button onClick={onLogout} className="p-1 transition-colors" style={{ color: 'var(--color-text-muted)' }}>
                            <LogOut className="w-4 h-4" />
                        </button>
                    </div>

                    {/* Mobile App Connection */}
                    <div className="mt-3 px-2 flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--color-surface-alt)' }}>
                        <div className="flex items-center gap-3">
                            <button onClick={onToggleServer}
                                    className="w-8 h-4 rounded-full transition-colors relative"
                                    style={{ background: serverStatus ? 'var(--color-success)' : 'var(--color-border)' }}>
                                <div className="absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full transition-transform"
                                     style={{ transform: serverStatus ? 'translateX(16px)' : 'translateX(0)' }} />
                            </button>
                            <span className="text-xs font-mono" style={{ color: 'var(--color-text-secondary)' }}>Mobile</span>
                        </div>
                        <button
                            onClick={() => serverStatus && setShowQRModal(true)}
                            disabled={!serverStatus}
                            className="transition-colors"
                            style={{ color: serverStatus ? 'var(--color-text-secondary)' : 'var(--color-border)', cursor: serverStatus ? 'pointer' : 'not-allowed' }}
                        >
                            <QrCode className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </aside>

            {/* QR Modal */}
            {showQRModal && (
                <div className="modal-overlay" onClick={() => setShowQRModal(false)}>
                    <div className="modal-content p-8 text-center" onClick={e => e.stopPropagation()}>
                        <button onClick={() => setShowQRModal(false)} className="absolute top-4 right-4" style={{ color: 'var(--color-text-muted)' }}>
                            <X className="w-5 h-5" />
                        </button>
                        <h3 className="text-xl font-semibold mb-2">Conectar Movil</h3>
                        <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>Escanea este codigo con tu dispositivo</p>
                        <div className="bg-white p-4 rounded-xl inline-block mb-6">
                            <QRCodeSVG value={`http://${window.location.hostname}:8001`} size={200} />
                        </div>
                        <div className="flex items-center justify-center gap-2 text-xs p-3 rounded-lg"
                             style={{ color: 'var(--color-text-muted)', background: 'var(--color-surface-alt)' }}>
                            <Wifi className="w-3 h-3" />
                            <span>Asegurate de estar en la misma red Wi-Fi</span>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Sidebar;
