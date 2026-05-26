import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/contexts/AuthContext';
import Layout from '@/components/Layout';
import RequireAuth from '@/components/RequireAuth';
import HomePage from '@/pages/HomePage';
import LoginPage from '@/pages/LoginPage';
import SignupPage from '@/pages/SignupPage';
import UploadPage from '@/pages/UploadPage';
import QuizPage from '@/pages/QuizPage';
import HistoryPage from '@/pages/HistoryPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />

            {/* Routes protégées */}
            <Route
              path="upload"
              element={
                <RequireAuth>
                  <UploadPage />
                </RequireAuth>
              }
            />
            <Route
              path="quiz/:id"
              element={
                <RequireAuth>
                  <QuizPage />
                </RequireAuth>
              }
            />
            <Route
              path="history"
              element={
                <RequireAuth>
                  <HistoryPage />
                </RequireAuth>
              }
            />

            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
