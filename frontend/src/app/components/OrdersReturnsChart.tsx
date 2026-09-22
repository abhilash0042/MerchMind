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

import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

export function OrdersReturnsChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        // Fetch last 365 days for a clearer bar chart view
        const response = await apiClient.get(`/analytics/orders/trend?seller_id=${sellerId}&days=365`);
        
        // Format dates for display
        const formattedData = response.data.map((item: any) => {
          const date = new Date(item.order_date);
          return {
            displayDate: date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }),
            orders: item.total_orders,
            cancelled: item.cancelled
          };
        });
        
        setData(formattedData);
      } catch (error) {
        console.error("Error fetching orders trend:", error);
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
          <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      )}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">
          Orders vs Cancellations
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Comparison of total orders and returns
        </p>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="displayDate"
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
          <Bar dataKey="orders" name="Orders" fill="#3B82F6" radius={[8, 8, 0, 0]} />
          <Bar dataKey="cancelled" name="Cancelled" fill="#EF4444" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
