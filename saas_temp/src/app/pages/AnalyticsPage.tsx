import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  Users,
  ShoppingBag,
  DollarSign,
  Target,
} from "lucide-react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from "recharts";

const trafficData = [
  { month: "Jan", organic: 4200, direct: 2400, referral: 1800, social: 1200 },
  { month: "Feb", organic: 4800, direct: 2600, referral: 2100, social: 1400 },
  { month: "Mar", organic: 5200, direct: 2800, referral: 2400, social: 1600 },
  { month: "Apr", organic: 5800, direct: 3200, referral: 2800, social: 1900 },
  { month: "May", organic: 6400, direct: 3600, referral: 3200, social: 2200 },
  { month: "Jun", organic: 7200, direct: 4000, referral: 3600, social: 2600 },
];

const deviceData = [
  { name: "Desktop", value: 58, color: "#8B5CF6" },
  { name: "Mobile", value: 35, color: "#3B82F6" },
  { name: "Tablet", value: 7, color: "#10B981" },
];

const topPages = [
  { page: "/products/electronics", views: 24500, bounceRate: "32%", avgTime: "4:23" },
  { page: "/products/fashion", views: 18200, bounceRate: "28%", avgTime: "5:12" },
  { page: "/products/home-decor", views: 15800, bounceRate: "35%", avgTime: "3:45" },
  { page: "/deals", views: 12400, bounceRate: "22%", avgTime: "6:15" },
  { page: "/new-arrivals", views: 9600, bounceRate: "30%", avgTime: "4:02" },
];

export function AnalyticsPage() {
  return (
    <>
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-600 mt-1">
          Detailed insights into your store performance
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-purple-50">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>12.5%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600">Total Visitors</p>
          <p className="text-3xl font-semibold text-gray-900 mt-1">48,574</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-blue-50">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>8.2%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600">Page Views</p>
          <p className="text-3xl font-semibold text-gray-900 mt-1">124,893</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-green-50">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            <div className="flex items-center gap-1 text-green-600 text-sm">
              <TrendingUp className="w-4 h-4" />
              <span>3.4%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600">Conversion Rate</p>
          <p className="text-3xl font-semibold text-gray-900 mt-1">3.24%</p>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 rounded-xl bg-amber-50">
              <ShoppingBag className="w-6 h-6 text-amber-600" />
            </div>
            <div className="flex items-center gap-1 text-red-600 text-sm">
              <TrendingDown className="w-4 h-4" />
              <span>2.1%</span>
            </div>
          </div>
          <p className="text-sm text-gray-600">Bounce Rate</p>
          <p className="text-3xl font-semibold text-gray-900 mt-1">42.8%</p>
        </div>
      </div>

      {/* Traffic Sources Chart */}
      <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Traffic Sources
        </h3>
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={trafficData}>
            <defs>
              <linearGradient id="organic" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="direct" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="referral" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="social" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" stroke="#9ca3af" style={{ fontSize: "12px" }} />
            <YAxis stroke="#9ca3af" style={{ fontSize: "12px" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
              }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
            <Area type="monotone" dataKey="organic" stackId="1" stroke="#8B5CF6" fill="url(#organic)" />
            <Area type="monotone" dataKey="direct" stackId="1" stroke="#3B82F6" fill="url(#direct)" />
            <Area type="monotone" dataKey="referral" stackId="1" stroke="#10B981" fill="url(#referral)" />
            <Area type="monotone" dataKey="social" stackId="1" stroke="#F59E0B" fill="url(#social)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Device Breakdown */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Device Breakdown
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={deviceData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={5}
                dataKey="value"
                label={(entry) => `${entry.value}%`}
              >
                {deviceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value) => <span className="text-sm text-gray-700">{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Pages */}
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Top Pages
          </h3>
          <div className="space-y-4">
            {topPages.map((page, index) => (
              <div key={index} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{page.page}</p>
                  <p className="text-xs text-gray-600 mt-1">
                    {page.views.toLocaleString()} views • {page.bounceRate} bounce • {page.avgTime} avg
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
