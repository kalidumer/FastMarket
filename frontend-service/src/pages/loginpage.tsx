import React, { useState, useEffect } from 'react';
import { useNavigate,Link} from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/store';
import { loginUser, clearAuthError } from '../features/auth/authSlice';
import { ROUTES } from '../config/constants';
import Input from "../components/input";
import Button from "../components/button";

export default function LoginPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const { token, loading, error } = useAppSelector((state) => state.auth);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    return () => {
      dispatch(clearAuthError());
    };
  }, [dispatch]);

  useEffect(() => {
    if (token) {
      navigate(ROUTES.HOME, { replace: true });
    }
  }, [token, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!email.trim() || !password.trim()) {
      setValidationError('Please fill in all fields.');
      return;
    }

    dispatch(loginUser({ email, password }));
  };

  return (
   <div className="flex bg-white min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-md space-y-8 rounded-xl bg-white shadow-md border border-gray-100 p-4">
            <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Create Account</h2>
                <p className="mt-2 text-sm text-gray-600">Join the platform to order products</p>
            </div>
            {(validationError || error) &&(
            <div className="rounded-md border border-red-600 bg-red-50 p-4 text-sm text-red-600 transition-all">
<p className="font-medium">{validationError || error}</p>
            </div>)}

            <form onSubmit={handleSubmit} className="space-y-4 mt-8 mx-4">
                
                <Input
                placeholder="Enter Your Email"
                type="email"
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                />
                <Input
                placeholder="Enter Your Password"
                type="password"
                value={password}
                onChange={(e)=>setPassword(e.target.value)}/>
               
                <Button type="submit">Sign In</Button>
            </form>
            <div className="text-center pt-4">
                <p className="text-sm text-gray-600">
                    If you have any account
                    <Link to="/signup" className="font-semibold px-2 text-indigo-500 hover:text-indigo-700">
                    Create Account Here</Link>
                </p>
            </div>
        </div>
    </div>
  );
}