import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Input } from '../components/common/Input.jsx';
import { Button } from '../components/common/Button.jsx';
import { useAuth } from '../hooks/useAuth.js';
import { registerAdmin } from '../api/client.js';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [regMessage, setRegMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const data = await login(username, password);
      navigate(data.role === 'admin' ? '/admin' : '/dashboard');
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegisterAdmin = async (e) => {
    e.preventDefault();
    setError('');
    setRegMessage('');
    setIsLoading(true);
    try {
      const data = await registerAdmin(username, password);
      localStorage.setItem('token', data.token);
      window.location.href = '/admin';
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
      <div className="w-full max-w-sm">
        <div className="bg-white rounded-xl border border-neutral-100 p-8">
          <h1 className="text-xl font-semibold text-neutral-900 mb-1">
            {isRegisterMode ? 'Регистрация (admin)' : 'Вход'}
          </h1>
          <p className="text-sm text-neutral-400 mb-6">Alien Signal Classifier</p>
          <form
            onSubmit={isRegisterMode ? handleRegisterAdmin : handleLogin}
            className="flex flex-col gap-4"
          >
            <Input
              label="Логин"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="username"
              autoFocus
            />
            <Input
              label="Пароль"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
            {regMessage && <p className="text-sm text-green-600">{regMessage}</p>}
            <Button type="submit" disabled={isLoading}>
              {isLoading
                ? (isRegisterMode ? 'Регистрация...' : 'Вход...')
                : (isRegisterMode ? 'Зарегистрироваться как admin' : 'Войти')
              }
            </Button>
          </form>
          <div className="mt-4 pt-4 border-t border-neutral-100">
            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setError('');
                setRegMessage('');
              }}
              className="w-full text-xs text-neutral-400 hover:text-neutral-600 transition-colors"
            >
              {isRegisterMode
                ? 'Назад ко входу'
                : 'Test: зарегистрироваться как admin'
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
