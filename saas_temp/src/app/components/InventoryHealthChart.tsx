import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from "recharts";

const data = [
  { name: "In Stock", value: 542, color: "#10B981" },
  { name: "Low Stock", value: 89, color: "#F59E0B" },
  { name: "Out of Stock", value: 24, color: "#EF4444" },
];

export function InventoryHealthChart() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Inventory Health
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Current stock status breakdown
        </p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={5}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => (
              <span className="text-sm text-gray-700">
                {value}: {entry.payload.value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
