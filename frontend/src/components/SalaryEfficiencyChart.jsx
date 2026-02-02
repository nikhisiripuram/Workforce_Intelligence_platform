import { Scatter } from "react-chartjs-2";
import { useEffect, useState } from "react";
import { getSalaryEfficiency } from "..src/api/analytics";

export default function SalaryEfficiencyChart({ runMonth }) {
  const [points, setPoints] = useState([]);

  useEffect(() => {
    getSalaryEfficiency(runMonth).then((res) =>
      setPoints(res.data.points)
    );
  }, [runMonth]);

  return (
    <Scatter
      data={{
        datasets: [
          {
            label: "Salary vs Efficiency",
            data: points.map((p) => ({
              x: p.salary,
              y: p.efficiency,
            })),
          },
        ],
      }}
    />
  );
}
