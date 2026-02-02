import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from "recharts";

const QuadrantChart = ({ data, onPointClick, height = 400 }) => {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <XAxis
          dataKey="hourly_rate"
          name="Hourly Cost"
          label={{ value: "Hourly Cost", position: "bottom", fill: "#94a3b8" }}
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8" }}
        />
        <YAxis
          dataKey="efficiency_score"
          name="Efficiency"
          label={{ value: "Efficiency", angle: -90, position: "left", fill: "#94a3b8" }}
          stroke="#94a3b8"
          tick={{ fill: "#94a3b8" }}
        />
        <Tooltip
          cursor={{ strokeDasharray: "3 3", stroke: "#475569" }}
          contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#f1f5f9' }}
        />
        <ReferenceLine x={40} stroke="#475569" strokeDasharray="3 3" />
        <ReferenceLine y={0.5} stroke="#475569" strokeDasharray="3 3" />
        <Scatter
          name="Employees"
          data={data}
          fill="#3b82f6"
          onClick={(point) => {
            // Recharts scatter click payload wraps provided data payload
            if (onPointClick && point?.payload?.employee_id) {
              onPointClick(point.payload.employee_id);
            }
          }}
          style={{ cursor: 'pointer' }}
        />
      </ScatterChart>
    </ResponsiveContainer>
  );
};

export default QuadrantChart;
