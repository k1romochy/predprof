import React from 'react';

export function Card({ title, children, className = '' }) {
  return (
    <div className={`bg-white rounded-xl border border-neutral-100 p-5 ${className}`}>
      {title && <h3 className="text-sm font-medium text-neutral-500 mb-4">{title}</h3>}
      {children}
    </div>
  );
}
