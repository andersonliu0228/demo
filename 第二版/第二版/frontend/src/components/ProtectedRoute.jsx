import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');

  // 若無有效 Token，導向登入頁
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
