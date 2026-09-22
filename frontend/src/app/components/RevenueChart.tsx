import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

const timeRanges = [
  { label: "30D", days: 30 },
  { label: "90D", days: 90 },
  { label: "1Y", days: 365 }
];

export function RevenueChart() {
  const [selectedRange, setSelectedRange] = useState(timeRanges[2]);
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const sellerId = await ensureSeller();
        const response = await apiClient.get(`/analytics/orders/trend?seller_id=${sellerId}&days=${selectedRange.days}`);
        
        // Format dates for display
        const formattedData = response.data.map((item: any) => {
          const date = new Date(item.order_date);
          return {
            ...item,
            displayDate: selectedRange.days <= 30 
              ? date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
              : date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
          };
        });
        
        setData(formattedData);
      } catch (error) {
        console.error("Error fetching revenue trend:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [selectedRange]);
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm relative">
      {loading && (
        <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
          <div className="animate-spin w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div>
        </div>
      )}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Revenue Trend</h3>
          <p className="text-sm text-gray-600 mt-1">
            Daily revenue performance
          </p>
        </div>
        
        {/* Date Range Filter */}
        <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-xl">
          {timeRanges.map((range) => (
            <button
              key={range.label}
              onClick={() => setSelectedRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedRange.label === range.label
                  ? "bg-white text-purple-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              {range.label}
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
            dataKey="displayDate"
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
          />
          <YAxis
            stroke="#9ca3af"
            style={{ fontSize: "12px" }}
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#fff",
              border: "1px solid #e5e7eb",
              borderRadius: "8px",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
            formatter={(value: number) => [`₹${value.toLocaleString()}`, "Revenue"]}
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