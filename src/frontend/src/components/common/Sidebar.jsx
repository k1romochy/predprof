import React from 'react';
import { NavLink } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth.js';

export function Sidebar() {
  const { user, logout } = useAuth();
  const isAdmin = user?.role === 'admin';

  const linkClass = ({ isActive }) =>
    `block px-4 py-2 rounded-lg text-sm transition-colors ${
      isActive
        ? 'bg-neutral-100 text-neutral-900 font-medium'
        : 'text-neutral-500 hover:text-neutral-900 hover:bg-neutral-50'
    }`;

  return (
    <aside className="w-56 h-screen fixed left-0 top-0 bg-white border-r border-neutral-100 flex flex-col">
      <div className="px-5 py-6">
        <h1 className="text-lg font-semibold text-neutral-900">Alien Signal</h1>
      </div>
      <nav className="flex-1 px-3 flex flex-col gap-1">
        {isAdmin ? (
          <NavLink to="/admin" className={linkClass}>Пользователи</NavLink>
        ) : (
          <NavLink to="/dashboard" className={linkClass}>Дашборд</NavLink>
        )}
        <NavLink to="/profile" className={linkClass}>Профиль</NavLink>
      </nav>
      <div className="px-3 pb-6">
        <div className="px-4 py-2 text-xs text-neutral-400 mb-2">
          {user?.first_name} {user?.last_name}
        </div>
        <button
          onClick={logout}
          className="w-full text-left px-4 py-2 rounded-lg text-sm text-neutral-500
            hover:text-red-500 hover:bg-red-50 transition-colors"
        >
          Выйти
        </button>
      </div>
    </aside>
  );
}
