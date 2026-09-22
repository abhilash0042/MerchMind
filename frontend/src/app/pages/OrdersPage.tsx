import {
  ShoppingCart,
  Search,
  Filter,
  Download,
  Eye,
  MoreVertical,
  Package,
  Truck,
  CheckCircle,
  XCircle,
} from "lucide-react";
import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

const orders = [
  { id: "ORD-2026-0847", customer: "Rahul Sharma", email: "rahul.s@email.com", items: 3, amount: "₹1,450", status: "Delivered", date: "Apr 1, 2026", payment: "Paid" },
  { id: "ORD-2026-0846", customer: "Priya Patel", email: "priya.p@email.com", items: 1, amount: "₹850", status: "Shipped", date: "Apr 1, 2026", payment: "Paid" },
  { id: "ORD-2026-0845", customer: "Arjun Reddy", email: "arjun.r@email.com", items: 5, amount: "₹3,420", status: "Processing", date: "Mar 31, 2026", payment: "Paid" },
  { id: "ORD-2026-0844", customer: "Neha Gupta", email: "neha.g@email.com", items: 2, amount: "₹1,200", status: "Pending", date: "Mar 31, 2026", payment: "Pending" },
  { id: "ORD-2026-0843", customer: "Vikram Singh", email: "vikram.s@email.com", items: 4, amount: "₹2,670", status: "Delivered", date: "Mar 30, 2026", payment: "Paid" },
  { id: "ORD-2026-0842", customer: "Anjali Desai", email: "anjali.d@email.com", items: 1, amount: "₹450", status: "Cancelled", date: "Mar 30, 2026", payment: "Refunded" },
  { id: "ORD-2026-0841", customer: "Rohan Verma", email: "rohan.v@email.com", items: 6, amount: "₹4,150", status: "Shipped", date: "Mar 29, 2026", payment: "Paid" },
  { id: "ORD-2026-0840", customer: "Sneha Iyer", email: "sneha.i@email.com", items: 2, amount: "₹1,350", status: "Processing", date: "Mar 29, 2026", payment: "Paid" },
];

const statusConfig = {
  Delivered: { bg: "bg-green-100", text: "text-green-700", icon: CheckCircle },
  Shipped: { bg: "bg-blue-100", text: "text-blue-700", icon: Truck },
  Processing: { bg: "bg-purple-100", text: "text-purple-700", icon: Package },
  Pending: { bg: "bg-amber-100", text: "text-amber-700", icon: Package },
  Cancelled: { bg: "bg-red-100", text: "text-red-700", icon: XCircle },
};

const orderStats = [
  { label: "Total Orders", value: "1,680", change: "+8.2% from last month", color: "purple" },
  { label: "Pending Orders", value: "124", change: "Needs attention", color: "amber" },
  { label: "Completed Orders", value: "1,402", change: "83.5% completion rate", color: "green" },
  { label: "Cancelled Orders", value: "154", change: "9.2% cancellation rate", color: "red" },
];

export function OrdersPage() {
  const [data, setData] = useState<any[]>(orders);
  const [stats, setStats] = useState(orderStats);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        
        // Fetch list and stats in parallel
        const [listRes, statsRes] = await Promise.all([
          apiClient.get(`/analytics/orders/list?seller_id=${sellerId}&limit=50`),
          apiClient.get(`/analytics/orders/stats?seller_id=${sellerId}&days=365`)
        ]);

        if (listRes.data && listRes.data.length > 0) {
          setData(listRes.data.map((item: any) => ({
            id: item.order_id,
            customer: item.customer_name,
            email: item.customer_email ? item.customer_email.replace(/(.{2}).+(@.+)/, '$1***$2') : 'No email',
            date: new Date(item.date).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }),
            status: item.status === 'delivered' ? 'Delivered' : item.status === 'cancelled' ? 'Cancelled' : item.status === 'processing' ? 'Processing' : item.status === 'shipped' ? 'Shipped' : 'Pending',
            amount: `₹${item.amount.toLocaleString()}`,
            items: item.items,
            payment: item.payment === 'cod' ? 'Pending' : 'Paid',
          })));
        }

        if (statsRes.stats && statsRes.stats.total_orders !== undefined) {
          const s = statsRes.stats;
          setStats([
            { label: "Total Orders", value: s.total_orders.toLocaleString(), change: "All time", color: "purple" },
            { label: "Pending Orders", value: s.pending_orders.toLocaleString(), change: "Awaiting fulfillment", color: "amber" },
            { label: "Completed Orders", value: s.delivered_orders.toLocaleString(), change: "Successfully delivered", color: "green" },
            { label: "Cancelled Orders", value: s.cancelled_orders.toLocaleString(), change: "Cancelled orders", color: "red" },
          ]);
        }
      } catch (error) {
        console.error("Error fetching orders data, using mock data", error);
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
            Orders {loading && <span className="text-sm font-normal text-gray-500">(Loading live data...)</span>}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage and track all your orders
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors">
          <Download className="w-4 h-4" />
          Export Orders
        </button>
      </div>

      {/* Order Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, index) => {
          const bgColor = stat.color === "purple" ? "bg-purple-50" : stat.color === "amber" ? "bg-amber-50" : stat.color === "green" ? "bg-green-50" : "bg-red-50";
          const iconColor = stat.color === "purple" ? "text-purple-600" : stat.color === "amber" ? "text-amber-600" : stat.color === "green" ? "text-green-600" : "text-red-600";
          
          return (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
              <div className={`p-3 rounded-xl ${bgColor} w-fit mb-4`}>
                <ShoppingCart className={`w-6 h-6 ${iconColor}`} />
              </div>
              <p className="text-sm text-gray-600">{stat.label}</p>
              <p className="text-3xl font-semibold text-gray-900 mt-1">{stat.value}</p>
              <p className="text-sm text-gray-600 mt-2">{stat.change}</p>
            </div>
          );
        })}
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-2xl shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search orders..."
                className="pl-10 pr-4 py-2 w-full bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
              />
            </div>
            <button className="flex items-center gap-2 px-4 py-2 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors">
              <Filter className="w-4 h-4" />
              Filter
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Order ID</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Customer</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Items</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Amount</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Status</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Payment</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Date</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.map((order) => {
                const statusInfo = statusConfig[order.status as keyof typeof statusConfig];
                const StatusIcon = statusInfo.icon;

                return (
                  <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <p className="font-medium text-gray-900">{order.id}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{order.customer}</p>
                        <p className="text-xs text-gray-600">{order.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">{order.items} items</td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{order.amount}</td>
                    <td className="px-6 py-4">
                      <span className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium w-fit ${statusInfo.bg} ${statusInfo.text}`}>
                        <StatusIcon className="w-3 h-3" />
                        {order.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        order.payment === "Paid" ? "bg-green-100 text-green-700" : 
                        order.payment === "Refunded" ? "bg-gray-100 text-gray-700" :
                        "bg-amber-100 text-amber-700"
                      }`}>
                        {order.payment}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">{order.date}</td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                          <Eye className="w-4 h-4 text-gray-600" />
                        </button>
                        <button className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                          <MoreVertical className="w-4 h-4 text-gray-600" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <p className="text-sm text-gray-600">Showing {data.length} orders</p>
          <div className="flex items-center gap-2">
            <button className="px-4 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 transition-colors">
              Previous
            </button>
            <button className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 transition-colors">
              Next
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
