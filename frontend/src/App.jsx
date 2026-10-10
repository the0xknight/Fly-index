import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
  Legend
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  Plane,
  Layers,
  Activity,
  RefreshCw,
  ShieldCheck,
  Calendar
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [timeseries, setTimeseries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeRoute, setActiveRoute] = useState('ALL');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [sumRes, tsRes] = await Promise.all([
        axios.get(`${API_BASE}/summary`),
        axios.get(`${API_BASE}/timeseries`)
      ]);
      setSummary(sumRes.data);
      setTimeseries(tsRes.data);
    } catch (err) {
      console.error(err);
      setError('Cannot connect to NAPI Engine backend. Ensure FastAPI is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', background: '#0f172a', color: '#94a3b8' }}>
        <RefreshCw className="animate-spin" style={{ marginRight: 8 }} /> Loading Airfare Index Engine Data...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: '#f87171' }}>
        <h2>Connection Error</h2>
        <p style={{ marginTop: 10, color: '#94a3b8' }}>{error}</p>
        <button
          onClick={fetchData}
          style={{ marginTop: 20, padding: '10px 20px', background: '#3b82f6', color: '#fff', borderRadius: 6 }}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  const isPositiveInflation = summary?.inflation_from_base_pct >= 0;

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '32px 24px' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28, flexWrap: 'wrap', gap: 16 }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: '#2563eb', padding: 8, borderRadius: 8, display: 'flex' }}>
              <Plane size={24} color="#fff" />
            </div>
            <div>
              <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.5px' }}>
                National Airfare Price Index (NAPI)
              </h1>
              <p style={{ fontSize: 13, color: '#94a3b8', marginTop: 2 }}>
                High-Frequency Domestic Aviation Price Tracker • Augmented for Consumer Price Index (CPI)
              </p>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', padding: '8px 14px', borderRadius: 8, fontSize: 13, color: '#38bdf8' }}>
            <ShieldCheck size={16} />
            <span>Jevons + Laspeyres Standard</span>
          </div>
          <button
            onClick={fetchData}
            style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#1e293b', border: '1px solid #334155', color: '#f8fafc', padding: '8px 14px', borderRadius: 8, fontSize: 13 }}
          >
            <RefreshCw size={15} /> Refresh
          </button>
        </div>
      </div>

      {/* KPI Headline Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 28 }}>
        {/* Card 1 */}
        <div style={{ background: '#1e293b', padding: 22, borderRadius: 12, border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 13 }}>
            <span>Composite National Index</span>
            <Activity size={18} color="#38bdf8" />
          </div>
          <div style={{ fontSize: 36, fontWeight: 800, marginTop: 8, letterSpacing: '-0.5px' }}>
            {summary?.current_index}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6, fontSize: 13, color: isPositiveInflation ? '#f87171' : '#4ade80' }}>
            {isPositiveInflation ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
            <span>{isPositiveInflation ? `+${summary?.inflation_from_base_pct}%` : `${summary?.inflation_from_base_pct}%`} vs Base (100.0)</span>
          </div>
        </div>

        {/* Card 2 */}
        <div style={{ background: '#1e293b', padding: 22, borderRadius: 12, border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 13 }}>
            <span>7-Day Price Velocity</span>
            <Layers size={18} color="#a855f7" />
          </div>
          <div style={{ fontSize: 36, fontWeight: 800, marginTop: 8, letterSpacing: '-0.5px' }}>
            {summary?.weekly_velocity_pct > 0 ? `+${summary?.weekly_velocity_pct}%` : `${summary?.weekly_velocity_pct}%`}
          </div>
          <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 6 }}>
            Rolling weekly momentum across all corridors
          </div>
        </div>

        {/* Card 3 */}
        <div style={{ background: '#1e293b', padding: 22, borderRadius: 12, border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 13 }}>
            <span>Top Inflation Contributor</span>
            <Plane size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: 26, fontWeight: 700, marginTop: 12, color: '#f59e0b' }}>
            {summary?.top_inflation_driver?.route}
          </div>
          <div style={{ color: '#f87171', fontSize: 13, marginTop: 8 }}>
            +{summary?.top_inflation_driver?.change_from_base_pct}% increase over reference period
          </div>
        </div>

        {/* Card 4 */}
        <div style={{ background: '#1e293b', padding: 22, borderRadius: 12, border: '1px solid #334155' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: 13 }}>
            <span>Reference Baseline Window</span>
            <Calendar size={18} color="#10b981" />
          </div>
          <div style={{ fontSize: 16, fontWeight: 600, marginTop: 16, color: '#f1f5f9' }}>
            {summary?.base_period}
          </div>
          <div style={{ color: '#94a3b8', fontSize: 13, marginTop: 8 }}>
            Base Index Standard: $P_0 = 100.0$
          </div>
        </div>
      </div>

      {/* Main Interactive Chart */}
      <div style={{ background: '#1e293b', padding: 24, borderRadius: 12, border: '1px solid #334155', marginBottom: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h3 style={{ fontSize: 18, fontWeight: 600 }}>Real-time Airfare Index Trajectory</h3>
            <p style={{ color: '#94a3b8', fontSize: 13, marginTop: 2 }}>
              Daily price movement normalized against the reference base period
            </p>
          </div>

          {/* Route Filter Buttons */}
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {['ALL', 'BOM-DEL', 'DEL-BOM', 'DEL-BLR', 'BLR-DEL'].map((route) => (
              <button
                key={route}
                onClick={() => setActiveRoute(route)}
                style={{
                  padding: '6px 12px',
                  borderRadius: 6,
                  fontSize: 12,
                  fontWeight: 500,
                  background: activeRoute === route ? '#2563eb' : '#0f172a',
                  color: activeRoute === route ? '#fff' : '#94a3b8',
                  border: '1px solid',
                  borderColor: activeRoute === route ? '#2563eb' : '#334155'
                }}
              >
                {route === 'ALL' ? 'Composite National' : route}
              </button>
            ))}
          </div>
        </div>

        <div style={{ width: '100%', height: 380 }}>
          <ResponsiveContainer>
            <LineChart data={timeseries} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#334155" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis domain={['dataMin - 5', 'dataMax + 5']} stroke="#64748b" tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 13 }}
                labelStyle={{ color: '#94a3b8', marginBottom: 4 }}
              />
              <Legend verticalAlign="top" height={36} />
              <ReferenceLine y={100} stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'Base Period (100.0)', fill: '#ef4444', fontSize: 12, position: 'right' }} />
              
              {activeRoute === 'ALL' ? (
                <Line
                  type="monotone"
                  dataKey="national_index"
                  name="National Airfare Index (Laspeyres)"
                  stroke="#38bdf8"
                  strokeWidth={3}
                  dot={false}
                />
              ) : (
                <Line
                  type="monotone"
                  dataKey={`idx_${activeRoute}`}
                  name={`${activeRoute} Route Index (Jevons)`}
                  stroke="#f59e0b"
                  strokeWidth={3}
                  dot={{ r: 2 }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Corridor Breakdown Table */}
      <div style={{ background: '#1e293b', padding: 24, borderRadius: 12, border: '1px solid #334155' }}>
        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Corridor-Level Inflation Contribution</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8', fontSize: 12, textTransform: 'uppercase' }}>
                <th style={{ padding: '12px 16px' }}>Corridor</th>
                <th style={{ padding: '12px 16px' }}>DGCA Weight ($w_r$)</th>
                <th style={{ padding: '12px 16px' }}>Elementary Method</th>
                <th style={{ padding: '12px 16px' }}>Inflation relative to Base</th>
                <th style={{ padding: '12px 16px' }}>Economic Impact</th>
              </tr>
            </thead>
            <tbody>
              {summary?.route_breakdown &&
                Object.entries(summary.route_breakdown).map(([route, delta]) => {
                  const weights = {
                    'BOM-DEL': '22%',
                    'DEL-BOM': '22%',
                    'DEL-BLR': '15%',
                    'BLR-DEL': '15%',
                    'BOM-BLR': '13%',
                    'BLR-BOM': '13%'
                  };
                  return (
                    <tr key={route} style={{ borderBottom: '1px solid #1e293b' }}>
                      <td style={{ padding: '14px 16px', fontWeight: 600 }}>{route}</td>
                      <td style={{ padding: '14px 16px', color: '#94a3b8' }}>{weights[route] || '10%'}</td>
                      <td style={{ padding: '14px 16px', color: '#38bdf8' }}>Jevons Geometric Mean</td>
                      <td style={{ padding: '14px 16px', color: delta >= 0 ? '#f87171' : '#4ade80', fontWeight: 600 }}>
                        {delta >= 0 ? `+${delta}%` : `${delta}%`}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: 4,
                          fontSize: 11,
                          background: delta > 15 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(56, 189, 248, 0.2)',
                          color: delta > 15 ? '#f87171' : '#38bdf8'
                        }}>
                          {delta > 15 ? 'High Inflation Driver' : 'Moderate Movement'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}