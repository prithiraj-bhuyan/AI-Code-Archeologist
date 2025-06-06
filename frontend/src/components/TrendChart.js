// TrendChart.js
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const TrendChart = ({ data, title }) => {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timeline" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="complexity" stroke="#8884d8" />
        <Line type="monotone" dataKey="debt" stroke="#82ca9d" />
        <Line type="monotone" dataKey="quality" stroke="#ffc658" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendChart;