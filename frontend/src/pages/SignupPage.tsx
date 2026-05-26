import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { signup } from '@/api/auth';
import { useAuth } from '@/contexts/AuthContext';
import { AxiosError } from 'axios';

export default function SignupPage() {
  const { refresh } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signup({ username, email, password });
      await refresh();
      navigate('/upload', { replace: true });
    } catch (err) {
      if (err instanceof AxiosError) {
        const data = err.response?.data;
        const firstError =
          data?.username?.[0] ??
          data?.email?.[0] ??
          data?.password?.[0] ??
          data?.detail ??
          'Inscription impossible.';
        setError(firstError);
      } else {
        setError('Erreur réseau.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="card">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Créer un compte</h1>
        <p className="text-sm text-slate-500 mb-6">
          Déjà inscrit ?{' '}
          <Link to="/login" className="text-indigo-600 hover:underline">
            Se connecter
          </Link>
        </p>

        {error && (
          <div className="mb-4 p-3 bg-rose-50 border-l-4 border-rose-500 text-sm text-rose-900 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Nom d'utilisateur
            </label>
            <input
              type="text"
              required
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Mot de passe
              <span className="text-slate-400 font-normal"> (≥ 8 caractères)</span>
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input"
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Création du compte…' : 'Créer mon compte'}
          </button>
        </form>
      </div>
    </div>
  );
}
