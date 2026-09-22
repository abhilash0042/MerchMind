import {
  Users,
  Search,
  Filter,
  Download,
  Mail,
  Phone,
  MapPin,
  Star,
  TrendingUp,
} from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const customers = [
  { id: "CUST-001", name: "John Smith", email: "john.smith@email.com", phone: "+1 (555) 123-4567", location: "New York, NY", orders: 24, spent: "$5,240", joined: "Jan 15, 2025", status: "VIP" },
  { id: "CUST-002", name: "Sarah Johnson", email: "sarah.j@email.com", phone: "+1 (555) 234-5678", location: "Los Angeles, CA", orders: 18, spent: "$3,890", joined: "Feb 8, 2025", status: "Regular" },
  { id: "CUST-003", name: "Michael Chen", email: "m.chen@email.com", phone: "+1 (555) 345-6789", location: "San Francisco, CA", orders: 32, spent: "$7,120", joined: "Dec 3, 2024", status: "VIP" },
  { id: "CUST-004", name: "Emily Davis", email: "emily.davis@email.com", phone: "+1 (555) 456-7890", location: "Chicago, IL", orders: 12, spent: "$2,450", joined: "Mar 20, 2025", status: "Regular" },
  { id: "CUST-005", name: "David Wilson", email: "d.wilson@email.com", phone: "+1 (555) 567-8901", location: "Boston, MA", orders: 28, spent: "$6,340", joined: "Nov 12, 2024", status: "VIP" },
  { id: "CUST-006", name: "Lisa Anderson", email: "lisa.a@email.com", phone: "+1 (555) 678-9012", location: "Seattle, WA", orders: 8, spent: "$1,780", joined: "Apr 5, 2025", status: "New" },
  { id: "CUST-007", name: "James Taylor", email: "james.t@email.com", phone: "+1 (555) 789-0123", location: "Miami, FL", orders: 15, spent: "$3,250", joined: "Jan 28, 2025", status: "Regular" },
  { id: "CUST-008", name: "Maria Garcia", email: "maria.g@email.com", phone: "+1 (555) 890-1234", location: "Austin, TX", orders: 21, spent: "$4,680", joined: "Feb 14, 2025", status: "Regular" },
];

const customerStats = [
  { label: "Total Customers", value: "2,847", change: "+124 this month", color: "purple" },
  { label: "Active Customers", value: "1,892", change: "66.5% active rate", color: "green" },
  { label: "New Customers", value: "284", change: "+18% from last month", color: "blue" },
  { label: "VIP Customers", value: "342", change: "12% of total", color: "amber" },
];

const customerGrowth = [
  { month: "Jan", customers: 2400 },
  { month: "Feb", customers: 2500 },
  { month: "Mar", customers: 2550 },
  { month: "Apr", customers: 2600 },
  { month: "May", customers: 2650 },
  { month: "Jun", customers: 2700 },
  { month: "Jul", customers: 2780 },
  { month: "Aug", customers: 2847 },
];

export function CustomersPage() {
  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Customers</h1>
          <p className="text-sm text-gray-600 mt-1">
            Manage and view customer information
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors">
          <Download className="w-4 h-4" />
          Export List
        </button>
      </div>

      {/* Customer Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {customerStats.map((stat, index) => {
          const bgColor = stat.color === "purple" ? "bg-purple-50" : stat.color === "green" ? "bg-green-50" : stat.color === "blue" ? "bg-blue-50" : "bg-amber-50";
          const iconColor = stat.color === "purple" ? "text-purple-600" : stat.color === "green" ? "text-green-600" : stat.color === "blue" ? "text-blue-600" : "text-amber-600";
          
          return (
            <div key={index} className="bg-white rounded-2xl p-6 shadow-sm">
              <div className={`p-3 rounded-xl ${bgColor} w-fit mb-4`}>
                <Users className={`w-6 h-6 ${iconColor}`} />
              </div>
              <p className="text-sm text-gray-600">{stat.label}</p>
              <p className="text-3xl font-semibold text-gray-900 mt-1">{stat.value}</p>
              <p className="text-sm text-gray-600 mt-2">{stat.change}</p>
            </div>
          );
        })}
      </div>

      {/* Customer Growth Chart */}
      <div className="bg-white rounded-2xl p-6 shadow-sm mb-8">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Customer Growth</h3>
          <p className="text-sm text-gray-600 mt-1">
            Total customers over time
          </p>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={customerGrowth}>
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
            <Bar dataKey="customers" fill="#8B5CF6" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Customers Table */}
      <div className="bg-white rounded-2xl shadow-sm">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search customers..."
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
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Customer</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Contact</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Location</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Orders</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Total Spent</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Status</th>
                <th className="text-left px-6 py-4 text-xs font-medium text-gray-600 uppercase tracking-wider">Joined</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                        {customer.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{customer.name}</p>
                        <p className="text-xs text-gray-600">{customer.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Mail className="w-4 h-4 text-gray-400" />
                        {customer.email}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Phone className="w-4 h-4 text-gray-400" />
                        {customer.phone}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-sm text-gray-700">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      {customer.location}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{customer.orders}</td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{customer.spent}</td>
                  <td className="px-6 py-4">
                    <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium w-fit ${
                      customer.status === "VIP" ? "bg-purple-100 text-purple-700" :
                      customer.status === "Regular" ? "bg-blue-100 text-blue-700" :
                      "bg-green-100 text-green-700"
                    }`}>
                      {customer.status === "VIP" && <Star className="w-3 h-3" />}
                      {customer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">{customer.joined}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="p-6 border-t border-gray-200 flex items-center justify-between">
          <p className="text-sm text-gray-600">Showing 8 of 2,847 customers</p>
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
