import { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import Kanban from './components/Kanban';
import NoteDetail from './components/NoteDetail';
import WebcamModal from './components/WebcamModal';
import Login from './components/Login';
import { setAuth, getUsers } from './api/client';
import { open } from '@tauri-apps/plugin-dialog';
import { X } from 'lucide-react';

function App() {
  const navigate = useNavigate();
  // Filter State
  const [activeFilter, setActiveFilter] = useState('all');
  const [showCompleted, setShowCompleted] = useState(false);
  const [isWebcamOpen, setIsWebcamOpen] = useState(false);

  // Server State
  const [serverStatus, setServerStatus] = useState(false);

  // User State
  const [users, setUsers] = useState<string[]>([]);
  const [fullUsers, setFullUsers] = useState<{ username: string, pin: string }[]>([]);
  const [currentUser, setCurrentUser] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'list' | 'add'>('list');
  const [newUsername, setNewUsername] = useState('');
  const [newPin, setNewPin] = useState('');

  useEffect(() => {
    // Fetch users on mount
    fetchUsers();
  }, []);

  useEffect(() => {
    if (currentUser && isAuthenticated) {
      // In a real app, you'd look up the PIN for the user.
      // For now, we use a default PIN or map it.
      const user = fullUsers.find(u => u.username === currentUser);
      const pin = user ? user.pin : '0295';
      setAuth(currentUser, pin);
    }
  }, [currentUser, fullUsers, isAuthenticated]);

  const fetchUsers = async () => {
    try {
      const userList = await getUsers();
      console.log("Users loaded from API:", userList);
      setFullUsers(userList);
      setUsers(userList.map(u => u.username));
      if (userList.length > 0 && !currentUser) {
        // Don't auto-login, let user choose
      }
    } catch (error) {
      console.error("Error fetching users from API:", error);
      console.log("Using fallback users from database...");
      // Fallback: Set default users if API fails
      const fallbackUsers = [
        { username: 'Beto May', pin: '0295' },
        { username: 'Alice Smith', pin: '1234' },
        { username: 'John Doe', pin: '5678' }
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

  const handleUpload = async () => {
    try {
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'Image',
          extensions: ['png', 'jpg', 'jpeg']
        }]
      });

      if (selected) {
        // In Tauri v2, selected is string or string[] or null
        const path = Array.isArray(selected) ? selected[0] : selected;
        if (path) {
          // Read file contents
          // Note: For web upload we need a File object, but here we are in Tauri.
          // The existing uploadImage expects a File object.
          // We might need to adjust this for Tauri or use a different method.
          // For now, let's just log.
          console.log("Selected file:", path);
          alert("Upload functionality needs adjustment for desktop file system access.");
        }
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername || !newPin) return;

    // Mock adding user for now since API might not support it yet
    // In a real app, await api.post('/users', { username: newUsername, pin: newPin })
    const newUser = { username: newUsername, pin: newPin };
    const updatedUsers = [...fullUsers, newUser];
    setFullUsers(updatedUsers);
    setUsers(updatedUsers.map(u => u.username));

    // Reset form
    setNewUsername('');
    setNewPin('');
    setActiveTab('list');
    alert(`Usuario ${newUsername} añadido correctamente (Localmente)`);
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
    <div className="flex h-screen bg-black text-white overflow-hidden font-sans selection:bg-blue-500/30">
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
      />

      <main className="flex-1 relative overflow-hidden bg-[#0f172a] m-2 rounded-3xl border border-white/5 shadow-2xl">
        <Routes>
          <Route path="/" element={
            <Dashboard
              activeFilter={activeFilter}
              showCompleted={showCompleted}
              currentUser={currentUser}
            />
          } />
          <Route path="/note/:id" element={<NoteDetail />} />
          <Route path="/kanban" element={<Kanban currentUser={currentUser} showCompleted={showCompleted} />} />
          <Route path="/settings" element={<div className="p-8">Configuración (Próximamente)</div>} />
        </Routes>
      </main>

      {isWebcamOpen && (
        <WebcamModal onClose={() => setIsWebcamOpen(false)} onCaptureComplete={() => setIsWebcamOpen(false)} />
      )}

      {/* User Management Modal */}
      {showUserModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in" onClick={() => setShowUserModal(false)}>
          <div className="bg-[#0f172a] border border-white/10 rounded-2xl p-8 shadow-2xl max-w-lg w-full relative" onClick={e => e.stopPropagation()}>
            <button
              onClick={() => setShowUserModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-bold text-white mb-6 font-display">Gestión de Usuarios</h3>

            {/* Tabs */}
            <div className="flex gap-4 mb-6 border-b border-white/10">
              <button
                onClick={() => setActiveTab('list')}
                className={`pb-2 text-sm font-bold uppercase tracking-wider transition-colors ${activeTab === 'list' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}
              >
                Usuarios
              </button>
              <button
                onClick={() => setActiveTab('add')}
                className={`pb-2 text-sm font-bold uppercase tracking-wider transition-colors ${activeTab === 'add' ? 'text-cyan-400 border-b-2 border-cyan-400' : 'text-gray-500 hover:text-gray-300'}`}
              >
                Añadir Nuevo
              </button>
            </div>

            {activeTab === 'list' ? (
              <div className="overflow-hidden rounded-xl border border-white/5 max-h-[400px] overflow-y-auto custom-scrollbar">
                <table className="w-full text-left text-sm text-gray-400">
                  <thead className="bg-white/5 text-gray-200 font-medium uppercase tracking-wider sticky top-0 bg-[#0f172a] z-10">
                    <tr>
                      <th className="px-6 py-3">Usuario</th>
                      <th className="px-6 py-3">PIN</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {fullUsers.map((user) => (
                      <tr key={user.username} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-black font-bold text-xs">
                            {user.username.charAt(0)}
                          </div>
                          {user.username}
                        </td>
                        <td className="px-6 py-4 font-mono text-blue-400 tracking-widest">{user.pin}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <form onSubmit={handleAddUser} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">Nombre de Usuario</label>
                  <input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="w-full bg-[#1a1b26] border border-gray-700 rounded p-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all"
                    placeholder="Ej. Juan Perez"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">PIN (4 dígitos)</label>
                  <input
                    type="text"
                    value={newPin}
                    onChange={(e) => setNewPin(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    className="w-full bg-[#1a1b26] border border-gray-700 rounded p-3 text-white focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none transition-all font-mono tracking-widest"
                    placeholder="0000"
                    required
                    minLength={4}
                    maxLength={4}
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-cyan-500 hover:bg-cyan-400 text-black font-bold py-3 rounded transition-colors mt-4"
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
