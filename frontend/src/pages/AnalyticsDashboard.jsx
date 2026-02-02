import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  fetchLatestRun,
  fetchDepartmentInsights,
  fetchQuadrantData,
  fetchDashboardSummary,
  fetchAllRuns,
  fetchDepartmentAIBrief,
  getDepartmentEfficiency,
} from "../api/analytics";

import QuadrantChart from "../components/QuadrantChart";
import EmptyState from "../components/EmptyState";
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

export default function AnalyticsDashboard() {
  const navigate = useNavigate();
  const [runMonth, setRunMonth] = useState(null);
  const [availableRuns, setAvailableRuns] = useState([]);
  const [summary, setSummary] = useState(null);
  const [deptEfficiency, setDeptEfficiency] = useState([]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // AI Brief State
  const [selectedDept, setSelectedDept] = useState(null);
  const [aiBrief, setAiBrief] = useState(null);
  const [briefLoading, setBriefLoading] = useState(false);

  useEffect(() => {
    Promise.all([fetchLatestRun(), fetchAllRuns()])
      .then(([latest, all]) => {
        setAvailableRuns(all);
        if (latest?.ready) {
          setRunMonth(latest.run_month);
        } else if (all.length > 0) {
          setRunMonth(all[0]);
        }
      })
      .catch(err => console.error("Initial load failed:", err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!runMonth) return;

    setLoading(true);
    Promise.all([
      fetchDepartmentInsights(runMonth),
      fetchQuadrantData(runMonth),
      fetchDashboardSummary(runMonth),
      getDepartmentEfficiency(runMonth)
    ])
      .then(([insightsRes, quadrantRes, summaryRes, efficiencyRes]) => {
        setData({
          ...insightsRes,
          quadrant: quadrantRes?.employees || []
        });
        setSummary(summaryRes);
        setDeptEfficiency(efficiencyRes.data || []);
      })
      .catch((err) => {
        console.error("Analytics load failed:", err);
      })
      .finally(() => setLoading(false));
  }, [runMonth]);

  const handleDeptClick = async (deptName) => {
    setSelectedDept(deptName);
    setAiBrief(null);
    setBriefLoading(true);
    try {
      const res = await fetchDepartmentAIBrief(deptName, runMonth);
      setAiBrief(res.brief);
    } catch (err) {
      setAiBrief("Failed to load AI briefing.");
    } finally {
      setBriefLoading(false);
    }
  };

  const handlePointClick = (employeeId) => {
    navigate(`/employee/${employeeId}/snapshot`);
  };

  if (loading && !summary) return (
    <div className="flex items-center justify-center min-h-screen bg-slate-900">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white p-6 relative">
      {/* Header */}
      <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Workforce Intelligence
          </h1>
          <div className="flex items-center gap-3 mt-2">
            <p className="text-slate-400">Payroll Run:</p>
            <select
              value={runMonth || ""}
              onChange={(e) => setRunMonth(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-3 py-1 text-blue-400 font-bold focus:ring-2 focus:ring-blue-500 outline-none"
            >
              {availableRuns.map(run => (
                <option key={run} value={run}>{run}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex gap-4">
          <Link
            to={`/org-tree?month=${runMonth}`}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition"
          >
            Org Structure
          </Link>
          <button
            onClick={() => navigate("/manager")}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 transition"
          >
            Manager Portal
          </button>
          <Link
            to="/upload"
            className="px-6 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg shadow-lg shadow-blue-500/30 transition transform hover:-translate-y-0.5"
          >
            Upload CSV
          </Link>
        </div>
      </header>

      {!runMonth ? (
        <EmptyState
          title="Insights Locked"
          message="Upload a payroll CSV to unlock workforce insights."
        />
      ) : (
        <div className="space-y-8">

          {/* Top Key Metrics Rows */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2">Total Monthly Payroll</h3>
              <p className="text-3xl font-black text-white">
                ${summary?.total_payroll ? (summary.total_payroll / 1000).toFixed(1) + 'k' : '0'}
                <span className="text-xs text-slate-500 font-normal ml-2 uppercase">USD / Month</span>
              </p>
            </div>
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2">Avg Efficiency</h3>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-black text-white">
                  {summary?.avg_performance || '0.0'}
                </p>
                <span className="text-xs text-slate-500 uppercase italic">vs Dept Baseline</span>
              </div>
            </div>
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700/50 backdrop-blur-sm">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-2">Headcount</h3>
              <p className="text-3xl font-black text-white">
                {summary?.headcount || '0'}
                <span className={`text-xs ml-3 font-bold px-2 py-0.5 rounded-full ${summary?.status === 'Stable' ? 'bg-green-900/30 text-green-400' : 'bg-purple-900/30 text-purple-400'}`}>
                  {summary?.status || 'Active'}
                </span>
              </p>
            </div>
          </div>

          {/* Charts Row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
              <h3 className="text-xl font-semibold mb-6">Department Efficiency Output</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={deptEfficiency}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="department" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} domain={[0, 1.2]} />
                    <Tooltip
                      cursor={{ fill: '#334155', opacity: 0.4 }}
                      contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                    />
                    <Bar dataKey="avg_efficiency" radius={[6, 6, 0, 0]}>
                      {deptEfficiency.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.avg_efficiency > 0.9 ? '#10b981' : '#3b82f6'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-2xl border border-slate-700 shadow-xl overflow-hidden">
              <h3 className="text-xl font-semibold mb-6">Talent Value Matrix</h3>
              <div className="h-[300px]">
                {data?.quadrant && (
                  <QuadrantChart
                    data={data.quadrant}
                    onPointClick={handlePointClick}
                    height={300}
                  />
                )}
              </div>
            </div>
          </div>

          {/* Department Insights */}
          <div className="bg-slate-800 p-8 rounded-3xl border border-slate-700 shadow-2xl">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-2xl font-bold text-white">Department Intelligence</h3>
              <span className="text-sm text-slate-500 italic">Click card for deep-dive analysis</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {data?.department_insights.map((d) => (
                <div
                  key={d.department}
                  onClick={() => handleDeptClick(d.department)}
                  className="bg-slate-900/40 p-6 rounded-2xl border border-slate-700/50 hover:border-blue-500/50 hover:bg-slate-700/20 cursor-pointer transition-all duration-300 group relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/5 blur-[40px] group-hover:bg-blue-500/10 transition-colors"></div>
                  <div className="flex justify-between items-start mb-4">
                    <h4 className="font-bold text-xl text-white group-hover:text-blue-400 transition">{d.department}</h4>
                    <span className="text-slate-500 text-xs font-mono uppercase">{d.headcount} Staff</span>
                  </div>
                  <ul className="text-slate-400 text-sm space-y-2 mb-4">
                    {d.insights.slice(0, 2).map((ins, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-blue-500/50">▶</span> {ins}
                      </li>
                    ))}
                  </ul>
                  <div className="pt-4 border-t border-slate-700/50 flex justify-between items-center">
                    <span className="text-blue-400 text-xs font-bold uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-opacity">AI Brief</span>
                    <svg className="w-4 h-4 text-slate-600 group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* AI Brief Modal */}
      {selectedDept && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-[2rem] w-full max-w-2xl shadow-2xl shadow-blue-500/10 overflow-hidden animate-in fade-in zoom-in duration-300">
            <div className="p-8 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
              <div>
                <h2 className="text-3xl font-black text-white">{selectedDept} Briefing</h2>
                <p className="text-blue-500 text-sm font-bold uppercase tracking-widest mt-1">Strategic Performance Review • {runMonth}</p>
              </div>
              <button
                onClick={() => setSelectedDept(null)}
                className="bg-slate-800 text-slate-400 hover:text-white h-10 w-10 rounded-full flex items-center justify-center transition shadow-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div className="p-10 max-h-[60vh] overflow-y-auto custom-scrollbar">
              {briefLoading ? (
                <div className="flex flex-col items-center gap-6 py-12 text-center">
                  <div className="relative">
                    <div className="absolute inset-0 rounded-full border-4 border-blue-500/20"></div>
                    <div className="h-16 w-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                  <div>
                    <p className="text-xl font-bold text-white mb-1 uppercase tracking-tighter">Analyzing Workforce Patterns</p>
                    <p className="text-slate-500 text-sm animate-pulse">Consulting AI workforce strategist...</p>
                  </div>
                </div>
              ) : (
                <div className="prose prose-invert max-w-none prose-p:text-slate-300 prose-p:leading-relaxed prose-strong:text-blue-400">
                  {aiBrief?.split('\n\n').map((para, i) => {
                    if (para.startsWith('###')) {
                      return <h3 key={i} className="text-xl font-bold text-white mb-4 mt-8 first:mt-0">{para.replace(/###\s*/, '')}</h3>
                    }
                    return (
                      <p key={i} className="mb-4 last:mb-0">
                        {para.split(/(\*\*.*?\*\*)/g).map((part, j) => {
                          if (part.startsWith('**') && part.endsWith('**')) {
                            return <strong key={j} className="text-blue-400">{part.slice(2, -2)}</strong>
                          }
                          return part;
                        })}
                      </p>
                    );
                  })}
                </div>
              )}
            </div>
            <div className="p-8 bg-slate-950/50 border-t border-slate-800 flex justify-end">
              <button
                onClick={() => setSelectedDept(null)}
                className="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl transition shadow-xl shadow-blue-600/20 active:scale-95"
              >
                Acknowledge Review
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Custom Scrollbar Styles */}
      <style dangerouslySetInnerHTML={{
        __html: `
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #475569; }
      `}} />
    </div>
  );
}
