import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3 text-slate-900 font-bold text-lg">
            <span className="w-8 h-8 grid place-items-center bg-indigo-600 text-white rounded font-mono">
              A
            </span>
            <span>
              EduTutor <span className="text-amber-500">IA</span>
            </span>
          </Link>

          <nav className="flex items-center gap-4 text-sm">
            {user ? (
              <>
                <Link to="/upload" className="text-slate-700 hover:text-indigo-600">
                  Nouveau quiz
                </Link>
                <Link to="/history" className="text-slate-700 hover:text-indigo-600">
                  Historique
                </Link>
                <span className="text-slate-500">|</span>
                <span className="text-slate-600 hidden sm:inline">{user.username}</span>
                <button onClick={handleLogout} className="btn-secondary">
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-slate-700 hover:text-indigo-600">
                  Connexion
                </Link>
                <Link to="/signup" className="btn-primary">
                  S'inscrire
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6 text-sm text-slate-500 flex flex-wrap items-center justify-between gap-3">
          <div>
            EduTutor IA — APOCAL'IPSSI 2026 ·
            <a
              href="https://mohamedelafrit.com/teaching/Master_Classe_Agile/cours.html"
              target="_blank"
              rel="noopener noreferrer"
              className="ml-1 text-indigo-600 hover:underline"
            >
              Cours Agile
            </a>
          </div>
          <div className="font-mono text-xs">CC BY-NC-SA 4.0</div>
        </div>
      </footer>
    </div>
  );
}
