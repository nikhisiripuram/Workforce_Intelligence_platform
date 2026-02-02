import { Bar } from "react-chartjs-2";
import { useEffect, useState } from "react";
import { getPeerDistribution } from "...src/api/analytics";

export default function PeerDistributionChart({ runMonth }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    getPeerDistribution(runMonth).then((res) =>
      setData(res.data.buckets)
    );
  }, [runMonth]);

  return (
    <Bar
      data={{
        labels: data.map((d) => d.range),
        datasets: [
          {
            label: "Employees",
            data: data.map((d) => d.count),
          },
        ],
      }}
    />
  );
}
