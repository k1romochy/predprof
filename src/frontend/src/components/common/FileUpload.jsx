import React, { useRef, useState } from 'react';

import { Button } from './Button.jsx';

export function FileUpload({ onFileSelect, accept = '.npz', isLoading = false }) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState('');

  const handleChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      onFileSelect(file);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      <Button
        variant="secondary"
        onClick={() => inputRef.current?.click()}
        disabled={isLoading}
      >
        {isLoading ? 'Загрузка...' : 'Выбрать файл'}
      </Button>
      {fileName && <span className="text-sm text-neutral-400">{fileName}</span>}
    </div>
  );
}
