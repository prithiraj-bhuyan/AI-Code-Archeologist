import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar } from 'recharts';
import { TrendingUp, Activity, Shield, Code, Zap, AlertTriangle } from 'lucide-react';

// Enhanced Trend Chart Component
const TrendChart = ({ data, title }) => {
  const colors = {
    complexity: '#8b5cf6',
    debt: '#ef4444',
    quality: '#10b981'
  };

  return (
    <div className="bg-gradient-to-br from-slate-50 to-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center space-x-2">
          <Activity className="w-5 h-5 text-purple-600" />
          <span>{title}</span>
        </h3>
        <div className="flex space-x-4 text-sm">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span className="text-gray-600">Complexity</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-gray-600">Tech Debt</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-600">Quality</span>
          </div>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis 
            dataKey="timeline" 
            stroke="#64748b"
            fontSize={12}
            tick={{ fill: '#64748b' }}
          />
          <YAxis 
            stroke="#64748b"
            fontSize={12}
            tick={{ fill: '#64748b' }}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Line 
            type="monotone" 
            dataKey="complexity" 
            stroke={colors.complexity}
            strokeWidth={3}
            dot={{ fill: colors.complexity, strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7, stroke: colors.complexity, strokeWidth: 2 }}
          />
          <Line 
            type="monotone" 
            dataKey="debt" 
            stroke={colors.debt}
            strokeWidth={3}
            dot={{ fill: colors.debt, strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7, stroke: colors.debt, strokeWidth: 2 }}
          />
          <Line 
            type="monotone" 
            dataKey="quality" 
            stroke={colors.quality}
            strokeWidth={3}
            dot={{ fill: colors.quality, strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7, stroke: colors.quality, strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

// Enhanced Architecture Overview Component
const ArchitectureOverviewChart = ({ data }) => {
  const getComplexityColor = (complexity) => {
    const colors = {
      'Low': '#10b981',
      'Medium': '#f59e0b',
      'High': '#ef4444',
      'Unknown': '#6b7280'
    };
    return colors[complexity] || colors['Unknown'];
  };

  const getPatternIcon = (pattern) => {
    return pattern === 'Unknown' ? AlertTriangle : Code;
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-white rounded-2xl p-6 border border-blue-200 shadow-sm hover:shadow-md transition-all duration-300 mt-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center space-x-2">
          <Shield className="w-5 h-5 text-blue-600" />
          <span>Architecture Overview</span>
        </h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {data.map((item, index) => {
          const Icon = getPatternIcon(item.pattern);
          return (
            <div key={index} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-600">{item.name}</span>
                <Icon className="w-4 h-4 text-gray-400" />
              </div>
              
              {item.complexity && (
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500">Complexity</span>
                    <span className="text-xs font-medium" style={{ color: getComplexityColor(item.complexity) }}>
                      {item.complexity}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="h-2 rounded-full transition-all duration-500"
                      style={{ 
                        backgroundColor: getComplexityColor(item.complexity),
                        width: item.complexity === 'Low' ? '33%' : item.complexity === 'Medium' ? '66%' : '100%'
                      }}
                    ></div>
                  </div>
                </div>
              )}
              
              {item.pattern && (
                <div>
                  <span className="text-xs text-gray-500">Pattern</span>
                  <div className="mt-1 px-2 py-1 bg-gray-100 rounded-md text-xs font-medium text-gray-700">
                    {item.pattern}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

// Enhanced Quality Metrics Component
const QualityMetricsChart = ({ data }) => {
  const COLORS = ['#10b981', '#3b82f6', '#ef4444'];
  
  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    if (score >= 4) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getIcon = (name) => {
    if (name.includes('Quality')) return Code;
    if (name.includes('Maintainability')) return Zap;
    return AlertTriangle;
  };

  // Transform data for radial chart
  const radialData = data.map((item, index) => ({
    name: item.name,
    value: (item.code_quality || item.maintainability || item.technical_debt || 0) * 10, // Scale to 0-100
    fill: COLORS[index % COLORS.length]
  }));

  return (
    <div className="bg-gradient-to-br from-green-50 to-white rounded-2xl p-6 border border-green-200 shadow-sm hover:shadow-md transition-all duration-300 mt-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-green-600" />
          <span>Quality Metrics</span>
        </h3>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Cards */}
        <div className="space-y-4">
          {data.map((item, index) => {
            const score = item.code_quality || item.maintainability || item.technical_debt || 0;
            const Icon = getIcon(item.name);
            
            return (
              <div key={index} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">{item.name}</span>
                  </div>
                  <div className={`px-2 py-1 rounded-lg text-xs font-bold ${getScoreColor(score)}`}>
                    {score}/10
                  </div>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div 
                    className="h-3 rounded-full transition-all duration-1000 ease-out"
                    style={{ 
                      backgroundColor: COLORS[index % COLORS.length],
                      width: `${(score / 10) * 100}%`
                    }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Radial Chart */}
        <div className="flex items-center justify-center">
          <ResponsiveContainer width="100%" height={250}>
            <RadialBarChart cx="50%" cy="50%" innerRadius="30%" outerRadius="80%" data={radialData}>
              <RadialBar 
                dataKey="value" 
                cornerRadius={10} 
                fill="#8884d8"
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value) => [`${(value/10).toFixed(1)}/10`, 'Score']}
              />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

// Main Enhanced Visualizations Component
const EnhancedVisualizations = ({ results }) => {
  if (!results || !results.visualizations) {
    return (
      <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200 text-center">
        <div className="text-gray-400 mb-2">
          <TrendingUp className="w-12 h-12 mx-auto" />
        </div>
        <p className="text-gray-600">No visualization data available</p>
      </div>
    );
  }

  const { visualizations } = results;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-2">
          <TrendingUp className="w-8 h-8" />
          <h2 className="text-3xl font-bold">Code Analytics</h2>
        </div>
        <p className="text-purple-100">Comprehensive insights into your codebase health and trends</p>
      </div>

      {/* Trend Chart */}
      {visualizations.trend_data && visualizations.trend_data.timeline && (
        <TrendChart
          data={visualizations.trend_data.timeline.map((week, index) => ({
            timeline: week,
            complexity: visualizations.trend_data.complexity_trend[index] || 0,
            debt: visualizations.trend_data.debt_trend[index] || 0,
            quality: visualizations.trend_data.quality_trend[index] || 0
          }))}
          title="Trends Over Time"
        />
      )}

      {/* Architecture Overview Chart */}
      {visualizations.architecture_overview && (
        <ArchitectureOverviewChart
          data={[
            { 
              name: 'System Architecture', 
              complexity: visualizations.architecture_overview.complexity || 'Unknown',
              pattern: visualizations.architecture_overview.pattern || 'Unknown'
            }
          ]}
        />
      )}

      {/* Quality Metrics Chart */}
      {visualizations.quality_metrics && (
        <QualityMetricsChart
          data={[
            { 
              name: 'Code Quality', 
              code_quality: visualizations.quality_metrics.code_quality || 0 
            },
            { 
              name: 'Maintainability', 
              maintainability: visualizations.quality_metrics.maintainability || 0 
            },
            { 
              name: 'Technical Debt', 
              technical_debt: visualizations.quality_metrics.technical_debt || 0 
            }
          ]}
        />
      )}
    </div>
  );
};

export default EnhancedVisualizations;