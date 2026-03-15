import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Brush,
} from 'recharts';

import { Card } from '../common/Card.jsx';
import { getTrainingHistory } from '../../api/client.js';
import { useAuth } from '../../hooks/useAuth.js';

export function TrainingHistoryChart() {
  const { token } = useAuth();
  const [data, setData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getTrainingHistory(token)
      .then((res) => {
        if (!cancelled) setData(res.epochs || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => { cancelled = true; };
  }, [token]);

  if (error) return <Card title="Точность по эпохам"><p className="text-sm text-red-500">{error}</p></Card>;
  if (!data.length) return <Card title="Точность по эпохам"><p className="text-sm text-neutral-400">Нет данных</p></Card>;

  return (
    <Card title="Точность по эпохам">
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="epoch" tick={{ fontSize: 12 }} stroke="#a3a3a3" />
          <YAxis tick={{ fontSize: 12 }} stroke="#a3a3a3" domain={[0, 1]} />
          <Tooltip
            contentStyle={{ border: '1px solid #e5e5e5', borderRadius: 8, fontSize: 12 }}
          />
          <Line
            type="monotone"
            dataKey="val_accuracy"
            stroke="#171717"
            strokeWidth={2}
            dot={false}
            name="Val Accuracy"
          />
          <Brush dataKey="epoch" height={24} stroke="#d4d4d4" fill="#fafafa" />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
