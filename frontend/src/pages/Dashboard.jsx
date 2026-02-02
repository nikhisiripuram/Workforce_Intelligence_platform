import { useEffect, useState } from "react";
import {
  fetchDepartmentInsights,
  fetchLatestRun
} from "../src/api/analytics";

import DepartmentInsightCard from "../src/components/DepartmentInsightCard";
import QuadrantChart from "../src/components/QuadrantChart";
import EmptyState from "../src/components/EmptyState";

import "./AnalyticsDashboard.css";

export default function AnalyticsDashboard() {
  const [runMonth, setRunMonth] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLatestRun()
      .then((res) => {
        if (!res.ready) {
          setRunMonth(null);
          return;
        }
        setRunMonth(res.run_month);
      })
      .catch(() => setError("Backend unreachable"));
  }, []);

  useEffect(() => {
    if (!runMonth) return;

    fetchDepartmentInsights(runMonth)
      .then(setData)
      .catch(() => setError("Analytics load failed"));
  }, [runMonth]);

  // 🟡 EMPTY STATE (this is what you asked for)
  if (runMonth === null) {
    return (
      <EmptyState
        title="No analytics available"
        description="Upload a payroll CSV and run payroll to unlock insights."
      />
    );
  }

  if (!data) return <p>Loading analytics…</p>;

  return (
    <div>
      <h2>Workforce Insights — {runMonth}</h2>

      <QuadrantChart data={data.quadrant_data} />

      <div className="grid">
        {data.department_insights.map((dept) => (
          <DepartmentInsightCard
            key={dept.department}
            dept={dept}
          />
        ))}
      </div>
    </div>
  );
}
