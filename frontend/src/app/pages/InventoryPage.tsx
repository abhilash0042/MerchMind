import {
  Package,
  Search,
  Filter,
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
} from "lucide-react";
import { useState, useEffect } from "react";
import { apiClient, ensureSeller } from "../services/api";

const inventoryItems = [
  { id: "INV-001", name: "Artisan Cold Brew Concentrate", sku: "BB-CF-001", category: "Cold Brew", stock: 245, minStock: 50, status: "In Stock", value: "₹85,500", lastUpdated: "2 hours ago" },
  { id: "INV-002", name: "Single-Origin Espresso Roast", sku: "BB-CF-002", category: "Whole Bean", stock: 89, minStock: 100, status: "Low Stock", value: "₹44,055", lastUpdated: "5 hours ago" },
  { id: "INV-003", name: "French Press Classic Blend", sku: "BB-CF-003", category: "Ground Coffee", stock: 0, minStock: 30, status: "Out of Stock", value: "₹0", lastUpdated: "1 day ago" },
  { id: "INV-004", name: "Pour Over Drip Bags (Pack of 10)", sku: "BB-CF-004", category: "Drip Bags", stock: 142, minStock: 20, status: "In Stock", value: "₹42,600", lastUpdated: "3 hours ago" },
  { id: "INV-005", name: "Vanilla Hazelnut Instant", sku: "BB-CF-005", category: "Instant Coffee", stock: 567, minStock: 100, status: "In Stock", value: "₹85,050", lastUpdated: "1 hour ago" },
  { id: "INV-006", name: "Decaf Colombian Roast", sku: "BB-CF-006", category: "Whole Bean", stock: 38, minStock: 50, status: "Low Stock", value: "₹18,620", lastUpdated: "4 hours ago" },
  { id: "INV-007", name: "Caramel Macchiato Blend", sku: "BB-CF-007", category: "Ground Coffee", stock: 198, minStock: 75, status: "In Stock", value: "₹89,100", lastUpdated: "6 hours ago" },
  { id: "INV-008", name: "Cold Brew Maker Kit", sku: "BB-CF-008", category: "Equipment", stock: 15, minStock: 40, status: "Low Stock", value: "₹45,000", lastUpdated: "8 hours ago" },
];

const stockSummary = [
  { label: "Total Items", value: "1,294", change: "+48 this week", icon: Package, color: "purple" },
  { label: "In Stock", value: "1,152", change: "89% of inventory", icon: CheckCircle, color: "green" },
  { label: "Low Stock", value: "118", change: "9% of inventory", icon: AlertTriangle, color: "amber" },
  { label: "Out of Stock", value: "24", change: "2% of inventory", icon: Clock, color: "red" },
];

export function InventoryPage() {
  const [data, setData] = useState<any[]>(inventoryItems);
  const [summary, setSummary] = useState(stockSummary);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const sellerId = await ensureSeller();
        
        // Fetch list and summary in parallel
        const [statusRes, summaryRes] = await Promise.all([
          apiClient.get(`/analytics/inventory/status?seller_id=${sellerId}`),
          apiClient.get(`/analytics/inventory/summary?seller_id=${sellerId}`)
        ]);

        if (statusRes.data && statusRes.data.length > 0) {
          setData(statusRes.data.map((item: any, idx: number) => ({
            id: String(item.product_id || item.sku || idx) + "-" + (item.marketplace || idx),
            name: item.product_name,
            sku: item.sku,
            category: item.category,
            stock: item.available_stock,
            minStock: item.reorder_threshold,
            status: item.available_stock === 0 ? "Out of Stock" : item.available_stock <= item.reorder_threshold ? "Low Stock" : "In Stock",
            value: "₹ -", // Not in this endpoint directly
            lastUpdated: new Date(item.snapshot_date).toLocaleDateString()
          })));
        }

        if (summaryRes.summary && summaryRes.summary.total_items !== undefined) {
          const s = summaryRes.summary;
          setSummary([
            { label: "Total Items", value: s.total_items.toLocaleString(), change: "Tracked products", icon: Package, color: "purple" },
            { label: "In Stock", value: s.in_stock.toLocaleString(), change: `${Math.round(s.in_stock/s.total_items*100 || 0)}% of inventory`, icon: CheckCircle, color: "green" },
            { label: "Low Stock", value: s.low_stock.toLocaleString(), change: `${Math.round(s.low_stock/s.total_items*100 || 0)}% of inventory`, icon: AlertTriangle, color: "amber" },
            { label: "Out of Stock", value: s.out_of_stock.toLocaleString(), change: `${Math.round(s.out_of_stock/s.total_items*100 || 0)}% of inventory`, icon: Clock, color: "red" },
          ]);
        }
      } catch (error) {
        console.error("Error fetching inventory data, using mock data", error);
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
            Inventory Management {loading && <span className="text-sm font-normal text-gray-500">(Loading live data...)</span>}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Track and manage your product inventory
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors">
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Stock Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {summary.map((item, index) => {
          const Icon = item.icon;
          const bgColor = item.color === "purple" ? "bg-purple-50" : item.color === "green" ? "bg-green-50" : item.color === "amber" ? "bg-amber-50" : "bg-red-50";
          const iconColor = item.color === "purple" ? "text-purple-600" : item.color === "green" ? "text-green-600" : item.color === "amber" ? "text-amber-600" : "text-red-600";
          
          return (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
              <div className={`p-3 rounded-xl ${bgColor} w-fit mb-4`}>
                <Icon className={`w-6 h-6 ${iconColor}`} />
              </div>
              <p className="text-sm text-gray-600">{item.label}</p>
              <p className="text-3xl font-semibold text-gray-900 mt-1">{item.value}</p>
              <p className="text-sm text-gray-600 mt-2">{item.change}</p>
            </div>
          );
        })}
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-2xl shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search inventory..."
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
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Product</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">SKU</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Category</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Stock</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Status</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Value</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Last Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-100 to-blue-100 rounded-lg flex items-center justify-center">
                        <Package className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{item.name}</p>
                        <p className="text-xs text-gray-600">{item.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">{item.sku}</td>
                  <td className="px-6 py-4">
                    <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                      {item.category}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{item.stock} units</p>
                      <p className="text-xs text-gray-600">Min: {item.minStock}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      item.status === "In Stock" ? "bg-green-100 text-green-700" :
                      item.status === "Low Stock" ? "bg-amber-100 text-amber-700" :
                      "bg-red-100 text-red-700"
                    }`}>
                      {item.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.value}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{item.lastUpdated}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <p className="text-sm text-gray-600">Showing {data.length} items</p>
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
