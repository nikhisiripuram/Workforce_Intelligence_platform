import axios from "axios";

/**
 * Single API client
 * Keep this as the ONLY place that knows backend baseURL
 */
const API = axios.create({
  baseURL: "http://127.0.0.1:8002",
});

export const fetchLatestRun = async () => {
  const res = await API.get("/runs/latest");
  return res.data;
};
/* =========================
   DASHBOARD / SUMMARY APIs
   ========================= */

/**
 * Department-level insight cards
 */
export const fetchDepartmentInsights = async (runMonth) => {
  const res = await API.get("/analytics/departments/insights", {
    params: { run_month: runMonth },
  });
  return res.data;
};

/**
 * High-level dashboard metrics (Payroll, Headcount, etc.)
 */
export const fetchDashboardSummary = async (runMonth) => {
  const res = await API.get("/analytics/summary", {
    params: { run_month: runMonth },
  });
  return res.data;
};

/**
 * List of available months for selection
 */
export const fetchAllRuns = async () => {
  const res = await API.get("/analytics/all-runs");
  return res.data;
};

/**
 * AI-powered strategic brief for a department
 */
export const fetchDepartmentAIBrief = async (department, runMonth) => {
  const res = await API.get("/ai/department/brief", {
    params: { department, run_month: runMonth },
  });
  return res.data;
};

/**
 * Quadrant chart (salary vs efficiency)
 */
export const fetchQuadrantData = async (runMonth) => {
  const res = await API.get("/analytics/quadrants", {
    params: { run_month: runMonth },
  });
  return res.data;
};

/* =========================
   CHART APIs
   ========================= */

export const getDepartmentEfficiency = async (runMonth) => {
  const res = await API.get("/analytics/charts/department-efficiency", {
    params: { run_month: runMonth },
  });
  return res.data;
};

export const getPeerDistribution = async (runMonth) => {
  const res = await API.get("/analytics/charts/peer-distribution", {
    params: { run_month: runMonth },
  });
  return res.data;
};

export const getSalaryEfficiency = async (runMonth) => {
  const res = await API.get("/analytics/charts/salary-vs-efficiency", {
    params: { run_month: runMonth },
  });
  return res.data;
};

/* =========================
   EMPLOYEE ANALYTICS
   ========================= */

export const fetchEmployeeInsights = async (employeeId, runMonth) => {
  const res = await API.get(`/analytics/employee/${employeeId}`, {
    params: { run_month: runMonth },
  });
  return res.data;
};

export const getEmployeeTrend = async (employeeId) => {
  const res = await API.get(`/analytics/charts/employee-trend/${employeeId}`);
  return res.data;
};

/* =========================
   AI SNAPSHOTS
   ========================= */

export const generateManagerReview = async (employeeId, runMonth) => {
  const res = await API.post(`/ai/snapshot/manager/${employeeId}`, null, {
    params: { run_month: runMonth },
  });
  return res.data; // { review: "..." }
};

export const generateIndividualFeedback = async (employeeId, runMonth) => {
  const res = await API.post(`/ai/snapshot/individual/${employeeId}`, null, {
    params: { run_month: runMonth },
  });
  return res.data; // { feedback: "..." }
};
