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
        <div className="min-h-screen bg-black flex items-center justify-center p-4">
            <div className="w-full max-w-[400px] mx-auto relative z-10">
                <div className="text-center mb-8">
                    <h1 className="font-display text-4xl md:text-5xl font-bold text-white mb-2 tracking-wider">PaperToPlan</h1>
                    <p className="text-gray-400 text-lg font-light">Inicia sesión para continuar</p>
                </div>

                <div className="bg-[#1a1b26] border border-gray-700 p-8 rounded-lg shadow-2xl shadow-cyan-500/10 relative overflow-hidden backdrop-blur-sm">
                    {/* Decorative top border */}
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-50"></div>

                    <form onSubmit={handleLogin} className="space-y-8">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2 font-mono">
                                USUARIO
                            </label>
                            <div className="relative group">
                                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                                <select
                                    value={selectedUser}
                                    onChange={(e) => {
                                        setSelectedUser(e.target.value);
                                        setError('');
                                    }}
                                    className="w-full pl-12 pr-12 py-3 bg-[#0c0d17] border border-gray-700 rounded-md focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 text-white outline-none transition-all font-mono appearance-none text-center"
                                    style={{ color: 'white', textAlign: 'center', textAlignLast: 'center' }}
                                    required
                                >
                                    <option value="" className="text-black bg-white">Selecciona un usuario</option>
                                    {users.map((user) => (
                                        <option key={user.username} value={user.username} className="text-black bg-white">
                                            {user.username}
                                        </option>
                                    ))}
                                </select>
                                <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                                    <div className="w-0 h-0 border-l-[5px] border-l-transparent border-r-[5px] border-r-transparent border-t-[6px] border-t-gray-500"></div>
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2 font-mono">
                                PIN
                            </label>
                            <div className="relative group">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-cyan-400 transition-colors" />
                                <input
                                    type="password"
                                    value={pin}
                                    onChange={(e) => {
                                        setPin(e.target.value);
                                        setError('');
                                    }}
                                    className="w-full pl-12 pr-12 py-3 bg-[#0c0d17] border border-gray-700 rounded-md focus:ring-1 focus:ring-cyan-500 focus:border-cyan-500 text-gray-200 outline-none transition-all font-mono placeholder-gray-600 text-center"
                                    style={{ textAlign: 'center' }}
                                    placeholder="Ingresa tu PIN"
                                    required
                                    maxLength={4}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="bg-red-900/20 border border-red-800/50 rounded px-4 py-3 text-red-400 text-sm font-mono flex items-center gap-2">
                                <span className="w-1.5 h-1.5 bg-red-500 rounded-full inline-block"></span>
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="w-full bg-cyan-500 text-black font-bold py-3 px-4 hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-[#1a1b26] focus:ring-cyan-500 transition-all duration-200 clip-path-angular font-display tracking-wide uppercase"
                        >
                            Iniciar Sesión
                        </button>
                    </form>
                </div>

                <div className="mt-8 text-center text-gray-600 text-xs font-mono">
                    PAPER_TO_PLAN_OS v2.0.4
                </div>
            </div>
        </div>
    );
};

export default Login;
