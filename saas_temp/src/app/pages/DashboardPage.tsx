import {
  DollarSign,
  ShoppingCart,
  TrendingUp,
  AlertTriangle,
  Wallet,
  RotateCcw,
  Users,
  Activity,
  Target,
  Clock,
  ArrowRight,
  ExternalLink,
} from "lucide-react";
import { KPICard } from "../components/KPICard";
import { RevenueChart } from "../components/RevenueChart";
import { OrdersReturnsChart } from "../components/OrdersReturnsChart";
import { InventoryHealthChart } from "../components/InventoryHealthChart";
import { MarketplaceRevenueChart } from "../components/MarketplaceRevenueChart";
import { AIInsights } from "../components/AIInsights";
import { MiniAnalyticsCard } from "../components/MiniAnalyticsCard";
import { Link } from "react-router";

const topProducts = [
  { id: "1", name: "Wireless Headphones Pro", sales: 1247, revenue: "$62,335", trend: "+12%" },
  { id: "2", name: "Smart Watch Series 5", sales: 892, revenue: "$44,600", trend: "+8%" },
  { id: "3", name: "Bluetooth Speaker Elite", sales: 756, revenue: "$37,800", trend: "+15%" },
];

export function DashboardPage() {
  return (
    <>
      {/* Overview Section - KPI Cards */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <KPICard
            title="Total Revenue"
            value="$148,250"
            change="+12.5% vs last month"
            changeType="positive"
            icon={DollarSign}
            iconColor="bg-gradient-to-br from-purple-500 to-purple-600"
            sparklineData={[45, 52, 48, 61, 55, 67, 72, 78, 85, 92, 88, 95]}
          />
          <KPICard
            title="Total Orders"
            value="1,680"
            change="+8.2% vs last month"
            changeType="positive"
            icon={ShoppingCart}
            iconColor="bg-gradient-to-br from-blue-500 to-blue-600"
            sparklineData={[1240, 1380, 1290, 1520, 1450, 1680, 1720, 1650, 1580, 1680, 1720, 1800]}
          />
          <KPICard
            title="Growth Rate"
            value="23.4%"
            change="+5.1% vs last month"
            changeType="positive"
            icon={TrendingUp}
            iconColor="bg-gradient-to-br from-green-500 to-green-600"
            sparklineData={[15, 17, 18, 19, 20, 21, 22, 23, 22, 23, 24, 23]}
          />
          <KPICard
            title="Inventory Alerts"
            value="24"
            change="3 critical items"
            changeType="negative"
            icon={AlertTriangle}
            iconColor="bg-gradient-to-br from-amber-500 to-amber-600"
            sparklineData={[35, 32, 30, 28, 26, 25, 24, 26, 25, 24, 23, 24]}
          />
          <KPICard
            title="Net Profit"
            value="$42,580"
            change="+14.3% vs last month"
            changeType="positive"
            icon={Wallet}
            iconColor="bg-gradient-to-br from-indigo-500 to-indigo-600"
            sparklineData={[25, 28, 30, 32, 35, 38, 40, 39, 41, 42, 43, 42]}
          />
          <KPICard
            title="Returns"
            value="125"
            change="-2.1% vs last month"
            changeType="positive"
            icon={RotateCcw}
            iconColor="bg-gradient-to-br from-teal-500 to-teal-600"
            sparklineData={[87, 102, 95, 118, 108, 125, 130, 128, 127, 125, 122, 125]}
          />
        </div>
      </section>

      {/* Revenue Chart - Full Width */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Analytics
        </h2>
        <RevenueChart />
      </section>

      {/* Report Analysis Grid */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Report Analysis
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <MiniAnalyticsCard
            title="Conversion Rate"
            value="3.24%"
            change="+0.4% from last week"
            changeType="positive"
            icon={Target}
            data={[2.1, 2.3, 2.5, 2.7, 2.9, 3.0, 3.1, 3.2]}
            chartType="area"
          />
          <MiniAnalyticsCard
            title="Avg. Order Value"
            value="$88.25"
            change="+$5.50 from last week"
            changeType="positive"
            icon={Activity}
            data={[75, 78, 80, 82, 84, 85, 87, 88]}
            chartType="line"
          />
          <MiniAnalyticsCard
            title="Active Customers"
            value="2,847"
            change="+124 from last week"
            changeType="positive"
            icon={Users}
            data={[2400, 2500, 2550, 2600, 2650, 2700, 2780, 2847]}
            chartType="area"
          />
          <MiniAnalyticsCard
            title="Avg. Response Time"
            value="2.4h"
            change="-0.3h from last week"
            changeType="positive"
            icon={Clock}
            data={[3.5, 3.2, 3.0, 2.9, 2.7, 2.6, 2.5, 2.4]}
            chartType="line"
          />
        </div>
      </section>

      {/* Two Column Grid - Additional Charts */}
      <section className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <OrdersReturnsChart />
          <InventoryHealthChart />
        </div>
      </section>

      {/* Top Products Section */}
      <section className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">
            Top Products
          </h2>
          <Link 
            to="/inventory" 
            className="text-sm text-purple-600 hover:text-purple-700 font-medium flex items-center gap-1"
          >
            View All
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {topProducts.map((product) => (
            <Link
              key={product.id}
              to={`/products/${product.id}`}
              className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-blue-100 rounded-xl flex items-center justify-center">
                  <ShoppingCart className="w-6 h-6 text-purple-600" />
                </div>
                <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-purple-600 transition-colors" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-3 group-hover:text-purple-600 transition-colors">
                {product.name}
              </h3>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Sales</span>
                  <span className="font-medium text-gray-900">{product.sales}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Revenue</span>
                  <span className="font-medium text-gray-900">{product.revenue}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Trend</span>
                  <span className="font-medium text-green-600 flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {product.trend}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Two Column Grid - Marketplace & AI Insights */}
      <section>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MarketplaceRevenueChart />
          <AIInsights />
        </div>
      </section>
    </>
  );
}