import { useState, useEffect, useRef } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Kanban from './components/Kanban';
import NoteDetail from './components/NoteDetail';
import WebcamModal from './components/WebcamModal';
import Login from './components/Login';
import { setAuth, getUsers, createUser, deleteUser, updateConfig, testConnection, uploadImage } from './api/client';
import { open } from '@tauri-apps/plugin-dialog';
import { X, Trash2, Settings, Save, Wifi } from 'lucide-react';

function App() {
  const navigate = useNavigate();
  // Filter State
  const [activeFilter, setActiveFilter] = useState('all');
  const [showCompleted, setShowCompleted] = useState(false);
  const [isWebcamOpen, setIsWebcamOpen] = useState(false);

  // Server State
  const [serverStatus, setServerStatus] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // User State
  const [users, setUsers] = useState<string[]>([]);
  const [fullUsers, setFullUsers] = useState<{ username: string, pin: string }[]>([]);
  const [currentUser, setCurrentUser] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'list' | 'add'>('list');
  const [newUsername, setNewUsername] = useState('');
  const [newPin, setNewPin] = useState('');

  // Config State
  const [config, setConfig] = useState({
    host: 'http://192.168.1.81:11434',
    logic_model: 'qwen3:8b',
    vision_model: 'qwen3-vl:8b'
  });
  const [configStatus, setConfigStatus] = useState('');
  const [mobileUrl, setMobileUrl] = useState(() => localStorage.getItem('mobileUrl') || `http://${window.location.hostname}:8001`);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'default');

  useEffect(() => {
    // Apply theme to body
    if (theme === 'cyberpunk') {
      document.body.classList.add('theme-cyberpunk');
    } else {
      document.body.classList.remove('theme-cyberpunk');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    // Fetch users on mount
    fetchUsers();
  }, []);

  useEffect(() => {
    if (currentUser && isAuthenticated) {
      const user = fullUsers.find(u => u.username === currentUser);
      const pin = user ? user.pin : '0295';
      setAuth(currentUser, pin);

      // Setup WebSocket for updates
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `ws://localhost:8001/ws/${encodeURIComponent(currentUser)}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket Connected');
        setServerStatus(true);
      };

      ws.onmessage = (event) => {
        console.log('WS Message:', event.data);
        if (event.data === 'processing_complete') {
          // Trigger refresh
          setRefreshTrigger(prev => prev + 1);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket Disconnected');
        setServerStatus(false);
      };

      return () => {
        ws.close();
      };
    }
  }, [currentUser, fullUsers, isAuthenticated]);

  const fetchUsers = async () => {
    try {
      const userList = await getUsers();
      console.log("Users loaded from API:", userList);
      setFullUsers(userList);
      setUsers(userList.map(u => u.username));
    } catch (error) {
      console.error("Error fetching users from API:", error);
      // Fallback
      const fallbackUsers = [
        { username: 'Beto May', pin: '0295' },
        { username: 'Alice Smith', pin: '1234' }
      ];
      setFullUsers(fallbackUsers);
      setUsers(fallbackUsers.map(u => u.username));
    }
  };

  const handleLoginSuccess = (username: string) => {
    setCurrentUser(username);
    setIsAuthenticated(true);
    navigate('/'); // Redirect to dashboard after successful login
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = () => {
    fileInputRef.current?.click();
  };

  const onFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      try {
        console.log("Uploading file:", file.name);
        await uploadImage(file);
        alert("Imagen subida correctamente. Procesando...");
        // Refresh or notify logic here if needed
      } catch (error) {
        console.error("Error uploading file:", error);
        alert("Error al subir la imagen.");
      }
    }
    // Reset input value to allow uploading the same file again
    if (event.target) {
      event.target.value = '';
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername || !newPin) return;

    try {
      await createUser(newUsername, newPin);
      await fetchUsers();
      setNewUsername('');
      setNewPin('');
      setActiveTab('list');
      alert(`Usuario ${newUsername} añadido correctamente`);
    } catch (error) {
      console.error("Error adding user:", error);
      alert("Error al añadir usuario");
    }
  };

  const handleDeleteUser = async (username: string) => {
    if (window.confirm(`¿Estás seguro de eliminar al usuario ${username}?`)) {
      try {
        await deleteUser(username);
        await fetchUsers();
      } catch (error) {
        console.error("Error deleting user:", error);
        alert("Error al eliminar usuario");
      }
    }
  };

  const handleSaveConfig = async () => {
    try {
      setConfigStatus('Guardando...');
      await updateConfig(config);
      localStorage.setItem('mobileUrl', mobileUrl);
      setConfigStatus('Configuración guardada');
      setTimeout(() => setConfigStatus(''), 3000);
    } catch (error) {
      console.error("Error saving config:", error);
      setConfigStatus('Error al guardar');
    }
  };

  const handleTestConnection = async () => {
    try {
      setConfigStatus('Probando...');
      const result = await testConnection();
      if (result.success) {
        setConfigStatus(`Conectado: ${result.models.length} modelos encontrados`);
      } else {
        setConfigStatus(`Error: ${result.errors.join(', ')}`);
      }
    } catch (error) {
      console.error("Error testing connection:", error);
      setConfigStatus('Error de conexión');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser('');
    navigate('/login');
  };

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="*" element={<Login users={fullUsers} onLoginSuccess={handleLoginSuccess} />} />
      </Routes>
    );
  }

  return (
    <div className="flex h-screen bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark overflow-hidden font-sans selection:bg-primary/30 transition-colors duration-300">
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileChange}
        className="hidden"
        accept="image/*"
      />
      <Sidebar
        onUpload={handleUpload}
        onWebcam={() => setIsWebcamOpen(true)}
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
        showCompleted={showCompleted}
        onToggleCompleted={() => setShowCompleted(!showCompleted)}
        serverStatus={serverStatus}
        onToggleServer={() => setServerStatus(!serverStatus)}
        users={users}
        currentUser={currentUser}
        onUserChange={setCurrentUser}
        onAddUser={() => alert("Función para añadir usuario próximamente")}
        onLogout={handleLogout}
        onShowUsers={() => setShowUserModal(true)}
        mobileUrl={mobileUrl}
      />

      <main className="flex-1 relative overflow-hidden bg-surface-light dark:bg-surface-dark m-2 rounded-3xl border border-border-light dark:border-border-dark shadow-2xl transition-colors duration-300">
        <Routes>
          <Route path="/" element={
            <Dashboard
              activeFilter={activeFilter}
              showCompleted={showCompleted}
              currentUser={currentUser}
              refreshTrigger={refreshTrigger}
            />
          } />
          <Route path="/note/:id" element={<NoteDetail />} />
          <Route path="/kanban" element={<Kanban currentUser={currentUser} showCompleted={showCompleted} />} />
          <Route path="/settings" element={
            <div className="p-8 max-w-4xl mx-auto">
              <h2 className="text-3xl font-bold mb-8 text-text-light dark:text-text-dark font-display">Configuración</h2>

              <div className="space-y-8">
                {/* Theme Settings */}
                <div className="bg-background-light dark:bg-background-dark rounded-2xl p-8 border border-border-light dark:border-border-dark shadow-lg">
                  <div className="flex items-center gap-3 mb-6 border-b border-border-light dark:border-border-dark pb-4">
                    <Settings className="w-6 h-6 text-primary" />
                    <h3 className="text-xl font-semibold text-text-light dark:text-text-dark">Apariencia</h3>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <label className="block font-medium text-text-light dark:text-text-dark">Modo Cyberpunk</label>
                      <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">Activa una interfaz futurista de alto contraste.</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={theme === 'cyberpunk'}
                        onChange={(e) => setTheme(e.target.checked ? 'cyberpunk' : 'default')}
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>

                {/* Mobile Server Config */}
                <div className="bg-background-light dark:bg-background-dark rounded-2xl p-8 border border-border-light dark:border-border-dark shadow-lg">
                  <div className="flex items-center gap-3 mb-6 border-b border-border-light dark:border-border-dark pb-4">
                    <Wifi className="w-6 h-6 text-green-400" />
                    <h3 className="text-xl font-semibold text-text-light dark:text-text-dark">Configuración de Servidor Móvil</h3>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">URL del Servidor (para QR)</label>
                      <p className="text-xs text-text-secondary-light dark:text-text-secondary-dark mb-2">Esta es la dirección que se codificará en el QR para que la app móvil se conecte.</p>
                      <input
                        type="text"
                        value={mobileUrl}
                        onChange={(e) => setMobileUrl(e.target.value)}
                        className="w-full bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary outline-none font-mono"
                        placeholder="http://192.168.1.x:8001"
                      />
                    </div>
                  </div>
                </div>

                {/* AI Config */}
                <div className="bg-background-light dark:bg-background-dark rounded-2xl p-8 border border-border-light dark:border-border-dark shadow-lg">
                  <div className="flex items-center gap-3 mb-6 border-b border-border-light dark:border-border-dark pb-4">
                    <Settings className="w-6 h-6 text-cyan-400" />
                    <h3 className="text-xl font-semibold text-text-light dark:text-text-dark">Configuración de IA (Ollama)</h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">Ollama Host</label>
                        <input
                          type="text"
                          value={config.host}
                          onChange={(e) => setConfig({ ...config, host: e.target.value })}
                          className="w-full bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">Logic Model</label>
                        <input
                          type="text"
                          value={config.logic_model}
                          onChange={(e) => setConfig({ ...config, logic_model: e.target.value })}
                          className="w-full bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">Vision Model</label>
                        <input
                          type="text"
                          value={config.vision_model}
                          onChange={(e) => setConfig({ ...config, vision_model: e.target.value })}
                          className="w-full bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary outline-none"
                        />
                      </div>
                    </div>

                    <div className="flex flex-col justify-end gap-4">
                      <button
                        onClick={handleTestConnection}
                        className="flex items-center justify-center gap-2 bg-surface-light dark:bg-surface-dark hover:bg-gray-200 dark:hover:bg-gray-700 text-text-light dark:text-text-dark border border-border-light dark:border-border-dark font-bold py-3 rounded transition-colors"
                      >
                        <Wifi className="w-5 h-5" />
                        Probar Conexión
                      </button>
                      <button
                        onClick={handleSaveConfig}
                        className="flex items-center justify-center gap-2 bg-primary hover:bg-primary/80 text-surface-dark font-bold py-3 rounded transition-colors"
                      >
                        <Save className="w-5 h-5" />
                        Guardar Configuración
                      </button>
                      {configStatus && (
                        <div className={`text-center p-2 rounded ${configStatus.includes('Error') ? 'bg-red-500/20 text-red-300' : 'bg-green-500/20 text-green-300'}`}>
                          {configStatus}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          } />
        </Routes>
      </main>

      {isWebcamOpen && (
        <WebcamModal onClose={() => setIsWebcamOpen(false)} onCaptureComplete={() => setIsWebcamOpen(false)} />
      )}

      {/* User Management Modal */}
      {showUserModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in" onClick={() => setShowUserModal(false)}>
          <div className="bg-surface-light dark:bg-surface-dark border border-border-light dark:border-border-dark rounded-2xl p-8 shadow-2xl max-w-lg w-full relative" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setShowUserModal(false)}
              className="absolute top-4 right-4 text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light dark:hover:text-text-dark transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-bold text-text-light dark:text-text-dark mb-6 font-display">Gestión de Usuarios</h3>

            {/* Tabs */}
            <div className="flex gap-4 mb-6 border-b border-border-light dark:border-border-dark">
              <button
                onClick={() => setActiveTab('list')}
                className={`pb-2 text-sm font-bold uppercase tracking-wider transition-colors ${activeTab === 'list' ? 'text-primary border-b-2 border-primary' : 'text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light'}`}
              >
                Usuarios
              </button>
              <button
                onClick={() => setActiveTab('add')}
                className={`pb-2 text-sm font-bold uppercase tracking-wider transition-colors ${activeTab === 'add' ? 'text-primary border-b-2 border-primary' : 'text-text-secondary-light dark:text-text-secondary-dark hover:text-text-light'}`}
              >
                Añadir Nuevo
              </button>
            </div>

            {activeTab === 'list' ? (
              <div className="overflow-hidden rounded-xl border border-border-light dark:border-border-dark max-h-[400px] overflow-y-auto custom-scrollbar">
                <table className="w-full text-left text-sm text-text-secondary-light dark:text-text-secondary-dark">
                  <thead className="bg-background-light dark:bg-background-dark text-text-light dark:text-text-dark font-medium uppercase tracking-wider sticky top-0 z-10">
                    <tr>
                      <th className="px-6 py-3">Usuario</th>
                      <th className="px-6 py-3">PIN</th>
                      <th className="px-6 py-3 text-right">Acciones</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-light dark:divide-border-dark">
                    {fullUsers.map((user) => (
                      <tr key={user.username} className="hover:bg-background-light dark:hover:bg-background-dark transition-colors">
                        <td className="px-6 py-4 font-medium text-text-light dark:text-text-dark flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-surface-dark font-bold text-xs">
                            {user.username.charAt(0)}
                          </div>
                          {user.username}
                        </td>
                        <td className="px-6 py-4 font-mono text-primary tracking-widest">{user.pin}</td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleDeleteUser(user.username)}
                            className="text-red-400 hover:text-red-300 p-1 hover:bg-red-500/10 rounded transition-colors"
                            title="Eliminar usuario"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <form onSubmit={handleAddUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">Nombre de Usuario</label>
                  <input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="w-full bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all"
                    placeholder="Ej. Juan Perez"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark mb-1">PIN (4 dígitos)</label>
                  <input
                    type="text"
                    value={newPin}
                    onChange={(e) => setNewPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    className="w-full bg-background-light dark:bg-background-dark border border-border-light dark:border-border-dark rounded p-3 text-text-light dark:text-text-dark focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all font-mono tracking-widest"
                    placeholder="0000"
                    required
                    minLength={4}
                    maxLength={4}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-primary hover:bg-primary/80 text-surface-dark font-bold py-3 rounded transition-colors mt-4"
                >
                  Guardar Usuario
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
