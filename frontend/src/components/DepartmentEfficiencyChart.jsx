import { Bar } from "react-chartjs-2";
import { useEffect, useState } from "react";
import { getDepartmentEfficiency } from "..src/api/analytics";

export default function DepartmentEfficiencyChart({ runMonth }) {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    getDepartmentEfficiency(runMonth)
      .then((data) => setRows(data.data))
      .catch(console.error);
  }, [runMonth]);

  return (
    <Bar
      data={{
        labels: rows.map((d) => d.department),
        datasets: [
          {
            label: "Avg Efficiency",
            data: rows.map((d) => d.avg_efficiency),
          },
        ],
      }}
    />
  );
}