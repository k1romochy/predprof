import React from 'react';

export function Input({ label, error, className = '', ...props }) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {label && <label className="text-sm text-neutral-500">{label}</label>}
      <input
        className="w-full px-3 py-2 rounded-lg border border-neutral-200 bg-white text-neutral-900
          text-sm outline-none focus:border-neutral-400 transition-colors placeholder:text-neutral-300"
        {...props}
      />
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
}
