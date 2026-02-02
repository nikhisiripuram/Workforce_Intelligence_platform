export default function DepartmentInsightCard({ dept }) {
  return (
    <div className="card">
      <h3>{dept.department}</h3>
      <p className="muted">
        Headcount: {dept.headcount}
      </p>

      <ul>
        {dept.insights.map((text, idx) => (
          <li key={idx}>{text}</li>
        ))}
      </ul>
    </div>
  );
}
