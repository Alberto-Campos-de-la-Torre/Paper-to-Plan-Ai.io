import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { setAuth } from '../api/client';

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
        <div className="flex items-center justify-center min-h-screen p-4 bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="font-display text-4xl md:text-5xl font-bold text-text-light dark:text-text-dark">PaperToPlan</h1>
                    <p className="text-text-secondary-light dark:text-text-secondary-dark mt-2 text-lg">Inicia sesión para continuar</p>
                </div>
                <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark p-8 md:p-10 rounded-lg shadow-2xl shadow-primary/10">
                    <form onSubmit={handleLogin} className="space-y-8">
                        <div>
                            <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-2" htmlFor="user">Usuario</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    id="user"
                                    name="user"
                                    value={selectedUser}
                                    onChange={(e) => {
                                        setSelectedUser(e.target.value);
                                        setError('');
                                    }}
                                    className="w-full px-4 py-3 bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded-md focus:ring-primary focus:border-primary text-text-light dark:text-text-dark"
                                    placeholder="Ingresa tu usuario"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-2" htmlFor="pin">PIN</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    id="pin"
                                    name="pin"
                                    value={pin}
                                    onChange={(e) => {
                                        setPin(e.target.value)
                                        setError('');
                                    }}
                                    className="w-full px-4 py-3 bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded-md focus:ring-primary focus:border-primary text-text-light dark:text-text-dark"
                                    placeholder="Ingresa tu PIN"
                                />
                            </div>
                        </div>
                        {error && (
                            <div className="bg-red-900/20 border border-red-800/50 rounded px-4 py-3 text-red-400 text-sm flex items-center gap-2">
                                {error}
                            </div>
                        )}
                        <div>
                            <button
                                type="submit"
                                className="w-full bg-primary text-background-dark font-bold py-3 px-4 rounded-md hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-surface-dark focus:ring-primary transition-opacity duration-200 clip-path-custom"
                            >
                                Iniciar Sesión
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default Login;
