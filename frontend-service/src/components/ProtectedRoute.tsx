import { Navigate, Outlet } from 'react-router-dom';
import { useAppSelector } from '../store/store';

export default function ProtectedRoute() {
  // Extract token specifically from state.auth
  const token = useAppSelector((state) => state.auth.token);

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}