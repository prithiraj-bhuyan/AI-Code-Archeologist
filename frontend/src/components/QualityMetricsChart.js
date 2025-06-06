// QualityMetricsChart.js
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const QualityMetricsChart = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="code_quality" fill="#8884d8" />
        <Bar dataKey="maintainability" fill="#82ca9d" />
        <Bar dataKey="technical_debt" fill="#ffc658" />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default QualityMetricsChart;