import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const data = [
  { month: "Jan", orders: 1240, returns: 87 },
  { month: "Feb", orders: 1380, returns: 102 },
  { month: "Mar", orders: 1290, returns: 95 },
  { month: "Apr", orders: 1520, returns: 118 },
  { month: "May", orders: 1450, returns: 108 },
  { month: "Jun", orders: 1680, returns: 125 },
];

export function OrdersReturnsChart() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Orders vs Returns
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Comparison of total orders and returns
        </p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="month"
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
          />
          <YAxis stroke="#9ca3af" style={{ fontSize: "12px" }} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
          />
          <Bar dataKey="orders" fill="#3B82F6" radius={[8, 8, 0, 0]} />
          <Bar dataKey="returns" fill="#EF4444" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
