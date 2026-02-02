import { Line } from "react-chartjs-2";
import { useEffect, useState } from "react";
import { getEmployeeTrend } from "..src/api/analytics";

export default function EmployeeTrendChart({ employeeId }) {
  const [trend, setTrend] = useState([]);

  useEffect(() => {
    getEmployeeTrend(employeeId)
      .then((data) => setTrend(data.trend))
      .catch(console.error);
  }, [employeeId]);

  return (
    <Line
      data={{
        labels: data.map((d) => d.run_month),
        datasets: [
          {
            label: "Efficiency",
            data: trend.map((d) => d.efficiency),
          },
        ],
      }}
    />
  );
}
