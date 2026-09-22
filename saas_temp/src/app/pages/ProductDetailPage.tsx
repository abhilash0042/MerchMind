import { useState } from "react";
import {
  ArrowLeft,
  Edit2,
  TrendingUp,
  DollarSign,
  ShoppingCart,
  Package,
  Zap,
  AlertCircle,
  CheckCircle,
} from "lucide-react";
import { Link } from "react-router";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";

// Performance data with diagnostic events
const performanceData = [
  { date: "Mar 1", unitsSold: 45, unitsReturned: 3, event: null },
  { date: "Mar 5", unitsSold: 52, unitsReturned: 4, event: null },
  { date: "Mar 10", unitsSold: 48, unitsReturned: 5, event: null },
  { date: "Mar 15", unitsSold: 38, unitsReturned: 6, event: "competitor_price" },
  { date: "Mar 20", unitsSold: 42, unitsReturned: 4, event: null },
  { date: "Mar 25", unitsSold: 65, unitsReturned: 3, event: "promotion" },
  { date: "Mar 30", unitsSold: 72, unitsReturned: 5, event: null },
];

// Competitor benchmarking data
const competitorData = [
  { metric: "Price", you: 49.99, comp1: 42.99, comp2: 54.99, comp3: 47.99 },
  { metric: "Rating", you: 4.7, comp1: 4.5, comp2: 4.3, comp3: 4.6 },
  { metric: "Reviews", you: 1240, comp1: 890, comp2: 2100, comp3: 750 },
];

// Sentiment data
const sentimentData = [
  { name: "Positive", value: 68, color: "#10B981" },
  { name: "Neutral", value: 22, color: "#6B7280" },
  { name: "Negative", value: 10, color: "#EF4444" },
];

const topReasons = [
  { phrase: "Excellent quality", sentiment: "positive", count: 342 },
  { phrase: "Fast shipping", sentiment: "positive", count: 298 },
  { phrase: "Misleading size", sentiment: "negative", count: 87 },
];

// Diagnostic event descriptions
const eventDescriptions = {
  competitor_price: {
    title: "Reason for Sales Drop",
    description:
      "AI detected a new competitor listing priced 15% lower and your 'Shipping Time' increased from 2 to 5 days.",
  },
  promotion: {
    title: "Reason for Sales Spike",
    description:
      "Your promotional campaign started, and AI identified increased social media engagement (+45%).",
  },
};

export function ProductDetailPage() {
  const [hoveredPoint, setHoveredPoint] = useState<any>(null);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const event = data.event ? eventDescriptions[data.event as keyof typeof eventDescriptions] : null;

      return (
        <div className="bg-white p-4 rounded-xl shadow-lg border border-gray-200 max-w-xs">
          <p className="font-semibold text-gray-900 mb-2">{data.date}</p>
          <div className="space-y-1 mb-3">
            <p className="text-sm text-gray-700">
              Units Sold: <span className="font-semibold text-indigo-600">{data.unitsSold}</span>
            </p>
            <p className="text-sm text-gray-700">
              Units Returned: <span className="font-semibold text-red-600">{data.unitsReturned}</span>
            </p>
          </div>
          {event && (
            <div className="pt-3 border-t border-gray-200">
              <p className="text-xs font-semibold text-gray-900 mb-1">{event.title}</p>
              <p className="text-xs text-gray-600">{event.description}</p>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      {/* Back Button */}
      <Link
        to="/"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        <span className="text-sm font-medium">Back to Dashboard</span>
      </Link>

      {/* Product Vital Header */}
      <div className="bg-white rounded-2xl p-8 shadow-sm mb-8">
        <div className="flex items-start justify-between gap-8">
          {/* Left: Product Info */}
          <div className="flex items-start gap-6">
            <div className="w-32 h-32 bg-gradient-to-br from-slate-100 to-slate-200 rounded-2xl flex items-center justify-center overflow-hidden">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop"
                alt="Wireless Headphones Pro"
                className="w-full h-full object-cover"
              />
            </div>
            <div>
              <h1 className="text-3xl font-semibold text-gray-900 mb-2">
                Wireless Headphones Pro
              </h1>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="font-medium">SKU: WHP-2024-01</span>
                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full font-medium">
                  Electronics
                </span>
              </div>
            </div>
          </div>

          {/* Right: KPI Cards */}
          <div className="flex gap-4">
            <div className="bg-gradient-to-br from-slate-50 to-white border border-slate-200 rounded-2xl p-5 min-w-[160px]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-slate-600 uppercase tracking-wide">
                  Current Price
                </p>
                <button className="p-1 hover:bg-slate-100 rounded transition-colors">
                  <Edit2 className="w-3 h-3 text-slate-500" />
                </button>
              </div>
              <p className="text-2xl font-semibold text-slate-900">$49.99</p>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-white border border-indigo-200 rounded-2xl p-5 min-w-[180px]">
              <p className="text-xs font-medium text-indigo-600 uppercase tracking-wide mb-2">
                Units Sold (30d)
              </p>
              <div className="flex items-end justify-between">
                <p className="text-2xl font-semibold text-slate-900">1,247</p>
                <div className="flex items-center gap-1 text-emerald-600 text-xs">
                  <TrendingUp className="w-3 h-3" />
                  <span>+12%</span>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-50 to-white border border-emerald-200 rounded-2xl p-5 min-w-[180px]">
              <p className="text-xs font-medium text-emerald-600 uppercase tracking-wide mb-2">
                Revenue Contrib.
              </p>
              <p className="text-2xl font-semibold text-slate-900">$62,335</p>
              <p className="text-xs text-slate-600 mt-1">12% of Total Store</p>
            </div>
          </div>
        </div>
      </div>

      {/* Performance & AI Advisor Row */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 mb-8">
        {/* Performance & Diagnostics (60%) */}
        <div className="lg:col-span-3 bg-white rounded-2xl p-8 shadow-sm">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-1">
              Performance & Diagnostics
            </h2>
            <p className="text-sm text-slate-600">
              Sales trends with AI-powered event detection
            </p>
          </div>
          <ResponsiveContainer width="100%" height={360}>
            <AreaChart
              data={performanceData}
              onMouseMove={(e: any) => {
                if (e && e.activePayload) {
                  setHoveredPoint(e.activePayload[0].payload);
                }
              }}
              onMouseLeave={() => setHoveredPoint(null)}
            >
              <defs>
                <linearGradient id="colorSold" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorReturned" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#EF4444" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="#EF4444" stopOpacity={0} />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: "12px" }} />
              <YAxis stroke="#94a3b8" style={{ fontSize: "12px" }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Area
                type="monotone"
                dataKey="unitsSold"
                stroke="#6366F1"
                strokeWidth={3}
                fill="url(#colorSold)"
                filter="url(#glow)"
                name="Units Sold"
              />
              <Area
                type="monotone"
                dataKey="unitsReturned"
                stroke="#EF4444"
                strokeWidth={2}
                fill="url(#colorReturned)"
                name="Units Returned"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* AI Co-Pilot Advisor (40%) */}
        <div className="lg:col-span-2 bg-gradient-to-br from-indigo-900 to-indigo-800 rounded-2xl p-8 shadow-lg">
          <div className="flex items-center gap-2 mb-6">
            <Zap className="w-6 h-6 text-yellow-400" />
            <h2 className="text-xl font-semibold text-white">AI Action Center</h2>
          </div>

          <div className="space-y-4">
            {/* Card 1: Price Optimization */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-5 border border-white/20">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-emerald-400/20 rounded-lg">
                  <DollarSign className="w-5 h-5 text-emerald-300" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">Price Optimization</h3>
                  <p className="text-sm text-indigo-100 leading-relaxed">
                    Increase price by 5% ($2.50). High demand elasticity detected. AI
                    predicts <span className="font-semibold text-emerald-300">+8% net profit</span>{" "}
                    without losing volume.
                  </p>
                </div>
              </div>
              <button className="w-full py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg text-sm font-medium transition-colors">
                Update Price
              </button>
            </div>

            {/* Card 2: Inventory Reorder */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-5 border border-white/20">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-amber-400/20 rounded-lg">
                  <Package className="w-5 h-5 text-amber-300" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">Inventory Reorder</h3>
                  <p className="text-sm text-indigo-100 leading-relaxed">
                    Restock 200 units by <span className="font-semibold">Apr 10</span>. 20% spike
                    predicted for next weekend. Current stock will run out in{" "}
                    <span className="font-semibold text-amber-300">12 days</span>.
                  </p>
                </div>
              </div>
              <button className="w-full py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition-colors">
                Restock Now
              </button>
            </div>

            {/* Card 3: Market Expansion */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-5 border border-white/20">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-blue-400/20 rounded-lg">
                  <ShoppingCart className="w-5 h-5 text-blue-300" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white mb-1">Bundle Opportunity</h3>
                  <p className="text-sm text-indigo-100 leading-relaxed">
                    Create a "Frequently Bought Together" bundle with{" "}
                    <span className="font-semibold">USB-C Cable Pro</span>.{" "}
                    <span className="font-semibold text-blue-300">88% affinity score</span> between
                    these items.
                  </p>
                </div>
              </div>
              <button className="w-full py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors">
                Create Bundle
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Market & Customer Row */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Competitor Benchmarking (60%) */}
        <div className="lg:col-span-3 bg-white rounded-2xl p-8 shadow-sm">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-1">
              Competitor Benchmarking
            </h2>
            <p className="text-sm text-slate-600">
              How you compare against top 3 marketplace competitors
            </p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={competitorData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" stroke="#94a3b8" style={{ fontSize: "12px" }} />
              <YAxis type="category" dataKey="metric" stroke="#94a3b8" style={{ fontSize: "12px" }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#fff",
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
              <Bar dataKey="you" fill="#6366F1" radius={[0, 4, 4, 0]} name="Your Product" />
              <Bar dataKey="comp1" fill="#94a3b8" radius={[0, 4, 4, 0]} name="Competitor 1" />
              <Bar dataKey="comp2" fill="#cbd5e1" radius={[0, 4, 4, 0]} name="Competitor 2" />
              <Bar dataKey="comp3" fill="#e2e8f0" radius={[0, 4, 4, 0]} name="Competitor 3" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Customer Sentiment (40%) */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-8 shadow-sm">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-1">Customer Sentiment</h2>
            <p className="text-sm text-slate-600">Analysis from 1,240 reviews</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={sentimentData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
                label={(entry) => `${entry.value}%`}
              >
                {sentimentData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          {/* Top Reasons */}
          <div className="mt-6 space-y-3">
            <h3 className="text-sm font-semibold text-slate-900 mb-3">Top Feedback Themes</h3>
            {topReasons.map((reason, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
              >
                <div className="flex items-center gap-2">
                  {reason.sentiment === "positive" ? (
                    <CheckCircle className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  )}
                  <span
                    className={`text-sm font-medium ${
                      reason.sentiment === "positive" ? "text-emerald-700" : "text-red-700"
                    }`}
                  >
                    {reason.phrase}
                  </span>
                </div>
                <span className="text-xs text-slate-600">{reason.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
