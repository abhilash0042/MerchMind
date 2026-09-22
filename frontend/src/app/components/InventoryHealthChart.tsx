import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

const COLORS = {
  inStock: "#10B981",
  lowStock: "#F59E0B",
  outOfStock: "#EF4444"
};

export function InventoryHealthChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        const response = await apiClient.get(`/analytics/inventory/status?seller_id=${sellerId}`);
        
        let inStock = 0;
        let lowStock = 0;
        let outOfStock = 0;
        
        response.data.forEach((item: any) => {
          if (item.available_stock === 0) {
            outOfStock += 1;
          } else if (item.available_stock <= item.reorder_threshold) {
            lowStock += 1;
          } else {
            inStock += 1;
          }
        });
        
        setData([
          { name: "In Stock", value: inStock, color: COLORS.inStock },
          { name: "Low Stock", value: lowStock, color: COLORS.lowStock },
          { name: "Out of Stock", value: outOfStock, color: COLORS.outOfStock },
        ]);
      } catch (error) {
        console.error("Error fetching inventory status:", error);
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
          Inventory Health
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          Current stock status breakdown across SKUs
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
          <Tooltip 
            contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)" }}
            formatter={(value: number) => [value, "SKUs"]}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => (
              <span className="text-sm text-gray-700">
                {value}: {entry.payload.value} SKUs
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
