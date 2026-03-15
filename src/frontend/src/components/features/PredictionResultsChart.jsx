import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Brush, Cell,
} from 'recharts';

import { Card } from '../common/Card.jsx';
import { getTestAccuracy } from '../../api/client.js';
import { useAuth } from '../../hooks/useAuth.js';

export function PredictionResultsChart() {
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getTestAccuracy(token)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => { cancelled = true; };
  }, [token]);

  if (error) return <Card title="Результаты предсказаний"><p className="text-sm text-red-500">{error}</p></Card>;
  if (!data?.predictions?.length) {
    return (
      <Card title="Результаты предсказаний">
        <p className="text-sm text-neutral-400">Загрузите .npz файл для получения результатов</p>
      </Card>
    );
  }

  const chartData = data.predictions.map((p) => ({
    index: p.index,
    confidence: p.confidence,
    isCorrect: p.correct,
  }));

  return (
    <Card title={`Результаты предсказаний — Accuracy: ${(data.accuracy * 100).toFixed(1)}%`}>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="index" tick={{ fontSize: 10 }} stroke="#a3a3a3" />
          <YAxis tick={{ fontSize: 12 }} stroke="#a3a3a3" domain={[0, 1]} />
          <Tooltip
            contentStyle={{ border: '1px solid #e5e5e5', borderRadius: 8, fontSize: 12 }}
            formatter={(value, name, entry) => [
              `${(value * 100).toFixed(1)}%`,
              entry.payload.isCorrect ? 'Верно' : 'Неверно',
            ]}
          />
          <Bar dataKey="confidence" name="Уверенность" radius={[2, 2, 0, 0]}>
            {chartData.map((entry, i) => (
              <Cell key={`cell-${i}`} fill={entry.isCorrect ? '#171717' : '#ef4444'} />
            ))}
          </Bar>
          <Brush dataKey="index" height={24} stroke="#d4d4d4" fill="#fafafa" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
