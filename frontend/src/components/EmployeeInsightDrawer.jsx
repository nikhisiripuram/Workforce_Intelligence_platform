import "./EmployeeInsightDrawer.css";

export default function EmployeeInsightDrawer({ data, onClose }) {
  if (!data) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer"
        onClick={(e) => e.stopPropagation()}
      >
        <header>
          <h3>{data.employee.name}</h3>
          <span>{data.employee.department}</span>
          <button onClick={onClose}>✕</button>
        </header>

        <p className="summary">{data.summary}</p>

        <section>
          <h4>Signals</h4>
          <ul>
            <li>Efficiency: {data.signals.efficiency_score}</li>
            <li>Peer Percentile: {data.signals.peer_percentile}</li>
            <li>Hourly Rate: ₹{data.signals.hourly_rate}</li>
          </ul>
        </section>

        <section>
          <h4>Risk Level</h4>
          <span className={`risk ${data.risk_flag.toLowerCase()}`}>
            {data.risk_flag}
          </span>
        </section>

        <section>
          <h4>Recommendations</h4>
          <ul>
            {data.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </section>
      </aside>
    </div>
  );
}
