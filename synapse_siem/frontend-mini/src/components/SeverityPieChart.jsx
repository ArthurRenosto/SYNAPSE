import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const severityColors = {
  critical: '#FF4C4C', // vermelho
  high: '#FFA500',     // laranja
  medium: '#FFD700',   // amarelo
  low: '#A9A9A9',      // cinza, opcional
};

const SeverityPieChart = ({ analysis }) => {
  if (!analysis) return null;

  const data = [
    { name: 'Critical', value: analysis.summary?.by_severity?.critical || 0, color: severityColors.critical },
    { name: 'High', value: analysis.summary?.by_severity?.high || 0, color: severityColors.high },
    { name: 'Medium', value: analysis.summary?.by_severity?.medium || 0, color: severityColors.medium },
    // opcional: Low
    // { name: 'Low', value: analysis.summary?.by_severity?.low || 0, color: severityColors.low },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={100}
          innerRadius={60} // cria efeito “doughnut” mais moderno
          paddingAngle={3} // separação entre fatias
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          labelLine={false} // remove linha do label para clean look
        >
          {data.map((entry, index) => (
            <Cell
              key={index}
              fill={entry.color}
              stroke="#fff"  // separação entre fatias
              strokeWidth={2}
            />
          ))}
        </Pie>
        <Tooltip
          formatter={(value) => [`${value} Findings`, 'Severity']}
          contentStyle={{ backgroundColor: '#1f1f1f', color: '#fff', borderRadius: '8px', border: 'none' }}
        />
        <Legend
          verticalAlign="bottom"
          iconType="circle"
          wrapperStyle={{ fontSize: '14px', fontWeight: 'bold' }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

export default SeverityPieChart;
