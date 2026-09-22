import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

export function MarketplaceRevenueChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        const response = await apiClient.get(`/analytics/revenue?seller_id=${sellerId}&days=365`);
        
        // Map data to the format expected by Recharts
        const formattedData = response.data.map((item: any) => ({
          marketplace: item.marketplace,
          revenue: item.net_revenue,
        }));
        
        setData(formattedData);
      } catch (error) {
        console.error("Error fetching marketplace revenue:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm relative">
      {loading && (
        <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-10 flex items-center justify-center rounded-2xl">
          <div className="animate-spin w-6 h-6 border-2 border-purple-500 border-t-transparent rounded-full"></div>
        </div>
      )}
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
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
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
            formatter={(value: number) => [`₹${value.toLocaleString()}`, "Revenue"]}
          />
          <Bar dataKey="revenue" fill="#8B5CF6" radius={[0, 8, 8, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
