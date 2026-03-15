import React from 'react';

import { Card } from '../components/common/Card.jsx';
import { Sidebar } from '../components/common/Sidebar.jsx';
import { useAuth } from '../hooks/useAuth.js';

export function ProfilePage() {
  const { user } = useAuth();

  const fields = [
    { label: 'ID', value: user?.id },
    { label: 'Логин', value: user?.username },
    { label: 'Имя', value: user?.first_name },
    { label: 'Фамилия', value: user?.last_name },
    { label: 'Роль', value: user?.role === 'admin' ? 'Администратор' : 'Пользователь' },
  ];

  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <main className="ml-56 p-8">
        <h2 className="text-lg font-semibold text-neutral-900 mb-6">Профиль</h2>
        <Card className="max-w-md">
          <div className="flex flex-col gap-4">
            {fields.map((f) => (
              <div key={f.label}>
                <p className="text-xs text-neutral-400">{f.label}</p>
                <p className="text-sm text-neutral-900">{f.value || '—'}</p>
              </div>
            ))}
          </div>
        </Card>
      </main>
    </div>
  );
}
