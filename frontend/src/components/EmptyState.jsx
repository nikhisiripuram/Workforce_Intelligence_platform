import { useNavigate } from "react-router-dom";

export default function EmptyState({ message }) {
  const navigate = useNavigate();

  return (
    <div style={{ padding: 40, textAlign: "center" }}>
      <h2>Insights Locked</h2>
      <p>{message}</p>

      <button onClick={() => navigate("/")}>
        Upload Payroll CSV
      </button>
    </div>
  );
}
