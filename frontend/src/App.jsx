import { Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import UploadPayrollPage from "./pages/UploadPayrollPage";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import EmployeeSnapshotPage from "./pages/EmployeeSnapshotPage";
import OrgTreePage from "./pages/OrgTreePage";
import ManagerPortal from "./pages/ManagerPortal";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/dashboard" element={<AnalyticsDashboard />} />
      <Route path="/upload" element={<UploadPayrollPage />} />
      <Route path="/manager" element={<ManagerPortal />} />
      <Route path="/org-tree" element={<OrgTreePage />} />
      <Route path="/employee/:id/snapshot" element={<EmployeeSnapshotPage />} />
    </Routes>
  );
}
