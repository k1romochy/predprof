import React, { useState } from 'react';

import { Card } from '../common/Card.jsx';
import { FileUpload } from '../common/FileUpload.jsx';
import { uploadPredict } from '../../api/client.js';
import { useAuth } from '../../hooks/useAuth.js';

export function UploadSection({ onUploadComplete }) {
  const { token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleFileSelect = async (file) => {
    setIsLoading(true);
    setError('');
    setResult(null);
    try {
      const data = await uploadPredict(token, file);
      setResult(data);
      if (onUploadComplete) onUploadComplete(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card title="Загрузка тестовых данных">
      <FileUpload onFileSelect={handleFileSelect} isLoading={isLoading} />
      {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      {result && (
        <div className="mt-4 flex gap-6">
          <div>
            <p className="text-xs text-neutral-400">Accuracy</p>
            <p className="text-2xl font-semibold text-neutral-900">
              {(result.accuracy * 100).toFixed(1)}%
            </p>
          </div>
          <div>
            <p className="text-xs text-neutral-400">Loss</p>
            <p className="text-2xl font-semibold text-neutral-900">
              {result.loss.toFixed(4)}
            </p>
          </div>
        </div>
      )}
    </Card>
  );
}
