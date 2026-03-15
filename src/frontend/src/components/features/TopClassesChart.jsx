import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';

import { Card } from '../common/Card.jsx';
import { getTopClasses } from '../../api/client.js';
import { useAuth } from '../../hooks/useAuth.js';

export function TopClassesChart() {
  const { token } = useAuth();
  const [data, setData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;
    getTopClasses(token)
      .then((res) => {
        if (!cancelled) setData(res.top_classes || []);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });
    return () => { cancelled = true; };
  }, [token]);

  if (error) return <Card title="Топ-5 классов"><p className="text-sm text-red-500">{error}</p></Card>;
  if (!data.length) return <Card title="Топ-5 классов"><p className="text-sm text-neutral-400">Нет данных</p></Card>;

  return (
    <Card title="Топ-5 классов (валидация)">
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis type="number" tick={{ fontSize: 12 }} stroke="#a3a3a3" />
          <YAxis
            type="category"
            dataKey="class_id"
            tick={{ fontSize: 12 }}
            stroke="#a3a3a3"
            width={60}
          />
          <Tooltip
            contentStyle={{ border: '1px solid #e5e5e5', borderRadius: 8, fontSize: 12 }}
          />
          <Bar dataKey="count" fill="#404040" radius={[0, 4, 4, 0]} name="Количество" />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
