import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Calendar,
  Download,
} from "lucide-react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, LineChart, Line } from "recharts";
import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

const monthlyRevenue = [
  { month: "Jan", revenue: 45000, profit: 18000, costs: 27000 },
  { month: "Feb", revenue: 52000, profit: 21500, costs: 30500 },
  { month: "Mar", revenue: 48000, profit: 19200, costs: 28800 },
  { month: "Apr", revenue: 61000, profit: 25500, costs: 35500 },
  { month: "May", revenue: 55000, profit: 22000, costs: 33000 },
  { month: "Jun", revenue: 67000, profit: 28500, costs: 38500 },
  { month: "Jul", revenue: 72000, profit: 31000, costs: 41000 },
  { month: "Aug", revenue: 78000, profit: 34000, costs: 44000 },
  { month: "Sep", revenue: 85000, profit: 37500, costs: 47500 },
  { month: "Oct", revenue: 92000, profit: 41000, costs: 51000 },
  { month: "Nov", revenue: 88000, profit: 38500, costs: 49500 },
  { month: "Dec", revenue: 95000, profit: 42580, costs: 52420 },
];

const revenueByCategory = [
  { category: "Whole Bean Coffee", revenue: 3420000 },
  { category: "Cold Brew", revenue: 2850000 },
  { category: "Merchandise", revenue: 1980000 },
  { category: "Equipment", revenue: 1560000 },
  { category: "Subscriptions", revenue: 1340000 },
  { category: "Gifts", revenue: 980000 },
];

const revenueMetrics = [
  { label: "Total Revenue", value: "₹14,825,000", change: "+12.5%", trend: "up", color: "purple" },
  { label: "Net Profit", value: "₹4,258,000", change: "+14.3%", trend: "up", color: "green" },
  { label: "Avg. Order Value", value: "₹850", change: "+5.2%", trend: "up", color: "blue" },
  { label: "Profit Margin", value: "28.7%", change: "-1.2%", trend: "down", color: "amber" },
];

export function RevenuePage() {
  const [trendData, setTrendData] = useState<any[]>(monthlyRevenue);
  const [categoryData, setCategoryData] = useState<any[]>(revenueByCategory);
  const [metrics, setMetrics] = useState<any[]>(revenueMetrics);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        
        // Fetch dashboard KPIs, category revenue, and monthly trend
        const [dashRes, catRes, trendRes] = await Promise.all([
          apiClient.get(`/analytics/dashboard?seller_id=${sellerId}&days=365`),
          apiClient.get(`/analytics/revenue/by-category?seller_id=${sellerId}&days=365`),
          apiClient.get(`/analytics/revenue/monthly?seller_id=${sellerId}&months=12`)
        ]);

        if (dashRes.kpis) {
          const rev = dashRes.kpis.total_net_revenue;
          const prevRev = rev * 0.88; // Simulated previous period
          const change = ((rev - prevRev) / prevRev * 100).toFixed(1);
          
          const profit = rev * 0.287; // Simulated margin for total metrics
          const avgOrder = dashRes.kpis.total_orders > 0 ? rev / dashRes.kpis.total_orders : 0;

          setMetrics([
            { label: "Total Revenue (30d)", value: `₹${rev.toLocaleString(undefined, {maximumFractionDigits:0})}`, change: `+${change}%`, trend: "up", color: "purple" },
            { label: "Net Profit (Est)", value: `₹${profit.toLocaleString(undefined, {maximumFractionDigits:0})}`, change: `+14.3%`, trend: "up", color: "green" },
            { label: "Avg. Order Value", value: `₹${avgOrder.toLocaleString(undefined, {maximumFractionDigits:0})}`, change: `+5.2%`, trend: "up", color: "blue" },
            { label: "Profit Margin", value: "28.7%", change: "-1.2%", trend: "down", color: "amber" },
          ]);
        }

        if (catRes.data && catRes.data.length > 0) {
          setCategoryData(catRes.data.slice(0, 6).map((item: any) => ({
            category: item.category,
            revenue: item.revenue
          })));
        }

        if (trendRes.data && trendRes.data.length > 0) {
          setTrendData(trendRes.data.map((item: any) => ({
            month: item.month,
            revenue: item.revenue,
            profit: item.profit,
            costs: item.costs
          })));
        }
      } catch (error) {
        console.error("Error fetching revenue data, using mock data", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Revenue {loading && <span className="text-sm font-normal text-gray-500">(Loading live data...)</span>}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Track your revenue and profitability metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
            <Calendar className="w-4 h-4" />
            Last 12 Months
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors">
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>
      </div>

      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric, index) => {
          const bgColor = metric.color === "purple" ? "bg-purple-50" : metric.color === "green" ? "bg-green-50" : metric.color === "blue" ? "bg-blue-50" : "bg-amber-50";
          const iconColor = metric.color === "purple" ? "text-purple-600" : metric.color === "green" ? "text-green-600" : metric.color === "blue" ? "text-blue-600" : "text-amber-600";
          const TrendIcon = metric.trend === "up" ? TrendingUp : TrendingDown;
          const trendColor = metric.trend === "up" ? "text-green-600" : "text-red-600";

          return (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${bgColor} w-fit`}>
                  <DollarSign className={`w-6 h-6 ${iconColor}`} />
                </div>
                <div className={`flex items-center gap-1 text-sm ${trendColor}`}>
                  <TrendIcon className="w-4 h-4" />
                  <span>{metric.change}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{metric.label}</p>
              <p className="text-3xl font-semibold text-gray-900 mt-1">{metric.value}</p>
            </div>
          );
        })}
      </div>

      {/* Revenue vs Profit Chart */}
      <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Revenue & Profit Trend</h3>
          <p className="text-sm text-gray-600 mt-1">
            Monthly comparison of revenue and net profit
          </p>
        </div>
        <ResponsiveContainer width="100%" height={360}>
          <AreaChart data={trendData}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#9ca3af" style={{ fontSize: "12px" }} />
            <YAxis stroke="#9ca3af" style={{ fontSize: "12px" }} tickFormatter={(value) => `₹${value / 1000}k`} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
              }}
              formatter={(value: number) => `₹${value.toLocaleString()}`}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
            <Area type="monotone" dataKey="revenue" stroke="#8B5CF6" strokeWidth={2} fill="url(#colorRevenue)" />
            <Area type="monotone" dataKey="profit" stroke="#10B981" strokeWidth={2} fill="url(#colorProfit)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue by Category */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Revenue by Category</h3>
            <p className="text-sm text-gray-600 mt-1">
              Top performing product categories
            </p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={categoryData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" stroke="#9ca3af" style={{ fontSize: "12px" }} tickFormatter={(value) => `₹${value / 1000}k`} />
              <YAxis type="category" dataKey="category" stroke="#9ca3af" style={{ fontSize: "12px" }} width={120} />
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

        {/* Cost Breakdown */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Monthly Costs</h3>
            <p className="text-sm text-gray-600 mt-1">
              Operating costs over time
            </p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="month" stroke="#9ca3af" style={{ fontSize: "12px" }} />
              <YAxis stroke="#9ca3af" style={{ fontSize: "12px" }} tickFormatter={(value) => `₹${value / 1000}k`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }}
                formatter={(value: number) => [`₹${value.toLocaleString()}`, "Costs"]}
              />
              <Line type="monotone" dataKey="costs" stroke="#EF4444" strokeWidth={2} dot={{ fill: "#EF4444" }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
