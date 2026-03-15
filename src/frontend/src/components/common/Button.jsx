import React from 'react';

export function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50';
  const variants = {
    primary: 'bg-neutral-900 text-white hover:bg-neutral-700',
    secondary: 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200 border border-neutral-200',
    danger: 'bg-red-500 text-white hover:bg-red-600',
  };

  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
