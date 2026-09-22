import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { marketplace: "Amazon", revenue: 45000 },
  { marketplace: "eBay", revenue: 28000 },
  { marketplace: "Shopify", revenue: 35000 },
  { marketplace: "Etsy", revenue: 18000 },
  { marketplace: "Walmart", revenue: 22000 },
];

export function MarketplaceRevenueChart() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Marketplace Revenue Split
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Revenue breakdown by sales channel
        </p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            type="number"
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
            tickFormatter={(value) => `$${value / 1000}k`}
          />
          <YAxis
            type="category"
            dataKey="marketplace"
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, "Revenue"]}
          />
          <Bar dataKey="revenue" fill="#8B5CF6" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
