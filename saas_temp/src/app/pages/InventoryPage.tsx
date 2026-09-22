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

const inventoryItems = [
  { id: "INV-001", name: "Wireless Headphones Pro", sku: "WHP-2024-01", category: "Electronics", stock: 245, minStock: 50, status: "In Stock", value: "$12,250", lastUpdated: "2 hours ago" },
  { id: "INV-002", name: "Smart Watch Series 5", sku: "SWS-2024-02", category: "Electronics", stock: 89, minStock: 100, status: "Low Stock", value: "$17,800", lastUpdated: "5 hours ago" },
  { id: "INV-003", name: "Leather Messenger Bag", sku: "LMB-2024-03", category: "Fashion", stock: 0, minStock: 30, status: "Out of Stock", value: "$0", lastUpdated: "1 day ago" },
  { id: "INV-004", name: "Ergonomic Office Chair", sku: "EOC-2024-04", category: "Furniture", stock: 142, minStock: 20, status: "In Stock", value: "$42,600", lastUpdated: "3 hours ago" },
  { id: "INV-005", name: "Ceramic Coffee Mug Set", sku: "CCM-2024-05", category: "Home", stock: 567, minStock: 100, status: "In Stock", value: "$8,505", lastUpdated: "1 hour ago" },
  { id: "INV-006", name: "Yoga Mat Premium", sku: "YMP-2024-06", category: "Sports", stock: 38, minStock: 50, status: "Low Stock", value: "$1,140", lastUpdated: "4 hours ago" },
  { id: "INV-007", name: "Bluetooth Speaker", sku: "BTS-2024-07", category: "Electronics", stock: 198, minStock: 75, status: "In Stock", value: "$9,900", lastUpdated: "6 hours ago" },
  { id: "INV-008", name: "Running Shoes Elite", sku: "RSE-2024-08", category: "Sports", stock: 15, minStock: 40, status: "Low Stock", value: "$1,950", lastUpdated: "8 hours ago" },
];

const stockSummary = [
  { label: "Total Items", value: "1,294", change: "+48 this week", icon: Package, color: "purple" },
  { label: "In Stock", value: "1,152", change: "89% of inventory", icon: CheckCircle, color: "green" },
  { label: "Low Stock", value: "118", change: "9% of inventory", icon: AlertTriangle, color: "amber" },
  { label: "Out of Stock", value: "24", change: "2% of inventory", icon: Clock, color: "red" },
];

export function InventoryPage() {
  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Inventory Management</h1>
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
        {stockSummary.map((item, index) => {
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
              {inventoryItems.map((item) => (
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
          <p className="text-sm text-gray-600">Showing 8 of 1,294 items</p>
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
