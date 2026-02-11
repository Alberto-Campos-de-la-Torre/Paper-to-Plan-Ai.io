import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Kanban from './components/Kanban';
import ConsultationDetail from './components/ConsultationDetail';
import PatientList from './components/PatientList';
import PatientDetail from './components/PatientDetail';
import Statistics from './components/Statistics';
import WebcamModal from './components/WebcamModal';
import TextNoteModal from './components/TextNoteModal';
import Login from './components/Login';
import { setAuth, getUsers, createUser, deleteUser } from './api/client';
import { open } from '@tauri-apps/plugin-dialog';
import { X } from 'lucide-react';

function App() {
  const navigate = useNavigate();
  const [activeFilter, setActiveFilter] = useState('all');
  const [showReviewed, setShowReviewed] = useState(false);
  const [isWebcamOpen, setIsWebcamOpen] = useState(false);
  const [isTextModalOpen, setIsTextModalOpen] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Server State
  const [serverStatus, setServerStatus] = useState(false);

  // User State
  const [fullUsers, setFullUsers] = useState<{ username: string; pin: string }[]>([]);
  const [currentUser, setCurrentUser] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'list' | 'add'>('list');
  const [newUsername, setNewUsername] = useState('');
  const [newPin, setNewPin] = useState('');

  // Refresh trigger
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetchUsers();
    const savedTheme = localStorage.getItem('megi-theme') as 'light' | 'dark' | null;
    if (savedTheme) setTheme(savedTheme);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('megi-theme', theme);
  }, [theme]);

  useEffect(() => {
    if (currentUser && isAuthenticated) {
      const user = fullUsers.find(u => u.username === currentUser);
      const pin = user ? user.pin : '';
      setAuth(currentUser, pin);
    }
  }, [currentUser, fullUsers, isAuthenticated]);

  const fetchUsers = async () => {
    try {
      const userList = await getUsers();
      setFullUsers(userList);
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  const handleLoginSuccess = (username: string) => {
    setCurrentUser(username);
    setIsAuthenticated(true);
    navigate('/');
  };

  const handleUpload = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [{ name: 'Image', extensions: ['png', 'jpg', 'jpeg'] }]
      });
      if (selected) {
        const path = Array.isArray(selected) ? selected[0] : selected;
        if (path) {
          console.log("Selected file:", path);
          alert("Documento seleccionado. Procesamiento iniciado.");
        }
      }
    } catch (error) {
      console.error(error);
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
    } catch (error) {
      console.error("Error creating user:", error);
      alert('Error al crear usuario');
    }
  };

  const handleDeleteUser = async (username: string) => {
    if (!window.confirm(`Eliminar usuario "${username}"?`)) return;
    try {
      await deleteUser(username);
      await fetchUsers();
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentUser('');
    navigate('/login');
  };

  const triggerRefresh = () => setRefreshKey(k => k + 1);

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="*" element={<Login users={fullUsers} onLoginSuccess={handleLoginSuccess} />} />
      </Routes>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden font-body" style={{ background: 'var(--color-bg)', color: 'var(--color-text)' }}>
      <Sidebar
        onUpload={handleUpload}
        onWebcam={() => setIsWebcamOpen(true)}
        onTextNote={() => setIsTextModalOpen(true)}
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
        showReviewed={showReviewed}
        onToggleReviewed={() => setShowReviewed(!showReviewed)}
        serverStatus={serverStatus}
        onToggleServer={() => setServerStatus(!serverStatus)}
        currentUser={currentUser}
        onLogout={handleLogout}
        onShowUsers={() => setShowUserModal(true)}
        theme={theme}
        onToggleTheme={() => setTheme(t => t === 'light' ? 'dark' : 'light')}
      />

      <main className="flex-1 relative overflow-hidden" style={{ background: 'var(--color-surface-alt)' }}>
        <Routes>
          <Route path="/" element={
            <Dashboard
              activeFilter={activeFilter}
              showReviewed={showReviewed}
              currentUser={currentUser}
              refreshKey={refreshKey}
            />
          } />
          <Route path="/consultation/:id" element={<ConsultationDetail />} />
          <Route path="/patients" element={<PatientList />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/kanban" element={<Kanban currentUser={currentUser} showReviewed={showReviewed} />} />
          <Route path="/settings" element={
            <Statistics currentUser={currentUser} />
          } />
        </Routes>
      </main>

      {isWebcamOpen && (
        <WebcamModal onClose={() => setIsWebcamOpen(false)} onCaptureComplete={() => { setIsWebcamOpen(false); triggerRefresh(); }} />
      )}

      {isTextModalOpen && (
        <TextNoteModal onClose={() => setIsTextModalOpen(false)} onCreated={() => { setIsTextModalOpen(false); triggerRefresh(); }} />
      )}

      {/* User Management Modal */}
      {showUserModal && (
        <div className="modal-overlay" onClick={() => setShowUserModal(false)}>
          <div className="modal-content p-6" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold">Gestion de Usuarios</h3>
              <button onClick={() => setShowUserModal(false)} style={{ color: 'var(--color-text-muted)' }}>
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex gap-4 mb-4" style={{ borderBottom: '1px solid var(--color-border-light)' }}>
              <button
                onClick={() => setActiveTab('list')}
                className="pb-2 text-sm font-semibold"
                style={{
                  color: activeTab === 'list' ? 'var(--color-primary)' : 'var(--color-text-muted)',
                  borderBottom: activeTab === 'list' ? '2px solid var(--color-primary)' : 'none'
                }}
              >
                Usuarios
              </button>
              <button
                onClick={() => setActiveTab('add')}
                className="pb-2 text-sm font-semibold"
                style={{
                  color: activeTab === 'add' ? 'var(--color-primary)' : 'var(--color-text-muted)',
                  borderBottom: activeTab === 'add' ? '2px solid var(--color-primary)' : 'none'
                }}
              >
                Nuevo Usuario
              </button>
            </div>

            {activeTab === 'list' ? (
              <div className="space-y-2 max-h-[300px] overflow-y-auto">
                {fullUsers.map(user => (
                  <div key={user.username} className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'var(--color-surface-alt)' }}>
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm" style={{ background: 'var(--color-primary)' }}>
                        {user.username.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium text-sm">{user.username}</p>
                        <p className="text-xs font-mono" style={{ color: 'var(--color-text-muted)' }}>{user.pin}</p>
                      </div>
                    </div>
                    <button onClick={() => handleDeleteUser(user.username)} className="text-xs btn btn-sm" style={{ color: 'var(--color-error)' }}>
                      Eliminar
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <form onSubmit={handleAddUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Nombre</label>
                  <input type="text" value={newUsername} onChange={e => setNewUsername(e.target.value)} className="input" placeholder="Dr. Juan Perez" required />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>PIN (4 digitos)</label>
                  <input type="text" value={newPin} onChange={e => setNewPin(e.target.value.replace(/\D/g, '').slice(0, 4))} className="input font-mono text-center" placeholder="0000" required minLength={4} maxLength={4} />
                </div>
                <button type="submit" className="btn btn-primary w-full">Guardar Usuario</button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
