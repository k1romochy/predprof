import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Brush,
} from 'recharts';

import { Card } from '../common/Card.jsx';
import { getClassDistribution } from '../../api/client.js';
import { useAuth } from '../../hooks/useAuth.js';

export function ClassDistributionChart() {
  const { token } = useAuth();
  const [data, setData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getClassDistribution(token)
      .then((res) => {
        if (!cancelled) setData(res.classes || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => { cancelled = true; };
  }, [token]);

  if (error) return <Card title="Распределение классов"><p className="text-sm text-red-500">{error}</p></Card>;
  if (!data.length) return <Card title="Распределение классов"><p className="text-sm text-neutral-400">Нет данных</p></Card>;

  return (
    <Card title="Распределение классов (обучающая выборка)">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="class_id" tick={{ fontSize: 12 }} stroke="#a3a3a3" />
          <YAxis tick={{ fontSize: 12 }} stroke="#a3a3a3" />
          <Tooltip
            contentStyle={{ border: '1px solid #e5e5e5', borderRadius: 8, fontSize: 12 }}
          />
          <Bar dataKey="count" fill="#171717" radius={[4, 4, 0, 0]} name="Количество" />
          <Brush dataKey="class_id" height={24} stroke="#d4d4d4" fill="#fafafa" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
