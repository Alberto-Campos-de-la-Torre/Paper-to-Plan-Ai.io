import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setAuth } from '../api/client';
import { User, Lock } from 'lucide-react';

interface LoginProps {
    users: { username: string; pin: string }[];
    onLoginSuccess: (username: string) => void;
}

const Login: React.FC<LoginProps> = ({ users, onLoginSuccess }) => {
    const [selectedUser, setSelectedUser] = useState('');
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedUser || !pin) {
            setError('Por favor selecciona un usuario e ingresa el PIN');
            return;
        }
        const user = users.find(u => u.username === selectedUser);
        if (user && user.pin === pin) {
            setAuth(selectedUser, pin);
            onLoginSuccess(selectedUser);
            navigate('/');
        } else {
            setError('PIN incorrecto');
            setPin('');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4" style={{ background: '#f5f3ee' }}>
            <div className="w-full max-w-[400px] mx-auto">
                <div className="text-center mb-8">
                    <h1 className="font-display text-4xl md:text-5xl font-bold mb-2" style={{ color: '#2d3b2d' }}>
                        MEGI Records
                    </h1>
                    <p className="font-brand text-sm tracking-wide" style={{ color: '#8b7355' }}>
                        Sistema de Expedientes Medicos Digitales
                    </p>
                </div>

                <div className="p-8 rounded-xl shadow-lg" style={{ background: '#ffffff', border: '1px solid #d4cfc7' }}>
                    <div className="h-1 -mt-8 -mx-8 mb-6 rounded-t-xl" style={{ background: 'linear-gradient(to right, #2d3b2d, #8b7355)' }} />

                    <form onSubmit={handleLogin} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium mb-2 font-brand" style={{ color: '#5a5a5a' }}>
                                USUARIO
                            </label>
                            <div className="relative">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" style={{ color: '#8a8a8a' }} />
                                <select
                                    value={selectedUser}
                                    onChange={(e) => { setSelectedUser(e.target.value); setError(''); }}
                                    className="input pl-12"
                                    style={{ textAlignLast: 'center' }}
                                    required
                                >
                                    <option value="">Selecciona un usuario</option>
                                    {users.map(user => (
                                        <option key={user.username} value={user.username}>{user.username}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2 font-brand" style={{ color: '#5a5a5a' }}>
                                PIN
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5" style={{ color: '#8a8a8a' }} />
                                <input
                                    type="password"
                                    value={pin}
                                    onChange={(e) => { setPin(e.target.value); setError(''); }}
                                    className="input pl-12 text-center font-mono"
                                    placeholder="Ingresa tu PIN"
                                    required
                                    maxLength={4}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="rounded-lg px-4 py-3 text-sm flex items-center gap-2"
                                 style={{ background: '#fde8e8', color: '#991b1b', border: '1px solid #fca5a5' }}>
                                <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: '#c0392b' }} />
                                {error}
                            </div>
                        )}

                        <button type="submit" className="btn btn-primary w-full py-3 font-brand text-base tracking-wide">
                            Iniciar Sesion
                        </button>
                    </form>
                </div>

                <div className="mt-6 text-center text-xs font-mono" style={{ color: '#8a8a8a' }}>
                    MEGI RECORDS v1.0.0
                </div>
            </div>
        </div>
    );
};

export default Login;
