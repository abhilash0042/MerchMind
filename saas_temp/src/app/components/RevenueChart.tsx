import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useState } from "react";

const data = [
  { month: "Jan", revenue: 45000 },
  { month: "Feb", revenue: 52000 },
  { month: "Mar", revenue: 48000 },
  { month: "Apr", revenue: 61000 },
  { month: "May", revenue: 55000 },
  { month: "Jun", revenue: 67000 },
  { month: "Jul", revenue: 72000 },
  { month: "Aug", revenue: 78000 },
  { month: "Sep", revenue: 85000 },
  { month: "Oct", revenue: 92000 },
  { month: "Nov", revenue: 88000 },
  { month: "Dec", revenue: 95000 },
];

const timeRanges = ["7D", "30D", "12M"];

export function RevenueChart() {
  const [selectedRange, setSelectedRange] = useState("30D");

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Revenue Trend</h3>
          <p className="text-sm text-gray-600 mt-1">
            Monthly revenue performance over the past year
          </p>
        </div>
        
        {/* Date Range Filter */}
        <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-xl">
          {timeRanges.map((range) => (
            <button
              key={range}
              onClick={() => setSelectedRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedRange === range
                  ? "bg-white text-purple-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="month"
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
            tickFormatter={(value) => `$${value / 1000}k`}
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
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#8B5CF6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorRevenue)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}