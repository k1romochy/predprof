import React, { useState } from 'react';

import { Card } from '../components/common/Card.jsx';
import { Input } from '../components/common/Input.jsx';
import { Button } from '../components/common/Button.jsx';
import { Sidebar } from '../components/common/Sidebar.jsx';
import { TrainingHistoryChart } from '../components/features/TrainingHistoryChart.jsx';
import { ClassDistributionChart } from '../components/features/ClassDistributionChart.jsx';
import { TopClassesChart } from '../components/features/TopClassesChart.jsx';
import { createUser } from '../api/client.js';
import { useAuth } from '../hooks/useAuth.js';

export function AdminPage() {
  const { token } = useAuth();
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    password: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setIsLoading(true);
    try {
      const user = await createUser(token, form);
      setMessage(`Пользователь ${user.username} создан`);
      setForm({ first_name: '', last_name: '', username: '', password: '' });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <main className="ml-56 p-8">
        <h2 className="text-lg font-semibold text-neutral-900 mb-6">Создание пользователя</h2>
        <Card className="max-w-md">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Имя"
              value={form.first_name}
              onChange={handleChange('first_name')}
              placeholder="Иван"
            />
            <Input
              label="Фамилия"
              value={form.last_name}
              onChange={handleChange('last_name')}
              placeholder="Иванов"
            />
            <Input
              label="Логин"
              value={form.username}
              onChange={handleChange('username')}
              placeholder="username"
            />
            <Input
              label="Пароль"
              type="password"
              value={form.password}
              onChange={handleChange('password')}
              placeholder="••••••••"
            />
            {error && <p className="text-sm text-red-500">{error}</p>}
            {message && <p className="text-sm text-green-600">{message}</p>}
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Создание...' : 'Создать'}
            </Button>
          </form>
        </Card>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mt-8">
          <TrainingHistoryChart />
          <ClassDistributionChart />
          <TopClassesChart />
        </div>
      </main>
    </div>
  );
}
