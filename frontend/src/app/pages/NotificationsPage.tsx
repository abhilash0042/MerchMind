import { Bell, Check, X, AlertTriangle, Info, CheckCircle, Package, DollarSign, TrendingUp } from "lucide-react";

const notifications = [
  {
    id: 1,
    type: "alert",
    icon: AlertTriangle,
    iconColor: "text-amber-600",
    bgColor: "bg-amber-50",
    title: "Low Stock Alert",
    message: "Single-Origin Espresso Roast has only 12 units remaining in stock",
    time: "5 minutes ago",
    read: false,
  },
  {
    id: 2,
    type: "success",
    icon: CheckCircle,
    iconColor: "text-green-600",
    bgColor: "bg-green-50",
    title: "Order Fulfilled",
    message: "Order #12847 has been successfully shipped via BlueDart",
    time: "1 hour ago",
    read: false,
  },
  {
    id: 3,
    type: "info",
    icon: Package,
    iconColor: "text-blue-600",
    bgColor: "bg-blue-50",
    title: "Inventory Restocked",
    message: "200 units of Artisan Cold Brew Concentrate have been added to inventory",
    time: "3 hours ago",
    read: true,
  },
  {
    id: 4,
    type: "success",
    icon: DollarSign,
    iconColor: "text-green-600",
    bgColor: "bg-green-50",
    title: "Revenue Milestone",
    message: "Congratulations! You've reached ₹1,500,000 in monthly revenue",
    time: "5 hours ago",
    read: true,
  },
  {
    id: 5,
    type: "alert",
    icon: AlertTriangle,
    iconColor: "text-red-600",
    bgColor: "bg-red-50",
    title: "Payment Failed",
    message: "Payment for Order #12839 was declined. Customer has been notified",
    time: "1 day ago",
    read: true,
  },
  {
    id: 6,
    type: "info",
    icon: TrendingUp,
    iconColor: "text-purple-600",
    bgColor: "bg-purple-50",
    title: "Sales Report Ready",
    message: "Your weekly coffee sales report is now available for download",
    time: "2 days ago",
    read: true,
  },
];

export function NotificationsPage() {
  return (
    <>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900">Notifications</h1>
          <p className="text-gray-600 mt-2">Stay updated with your store activity</p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
            Mark All as Read
          </button>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
            Settings
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Unread</p>
              <p className="text-3xl font-semibold text-gray-900">2</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center">
              <Bell className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Today</p>
              <p className="text-3xl font-semibold text-gray-900">4</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Info className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">This Week</p>
              <p className="text-3xl font-semibold text-gray-900">12</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Notifications List */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="divide-y divide-gray-200">
          {notifications.map((notification) => {
            const Icon = notification.icon;
            return (
              <div
                key={notification.id}
                className={`p-6 hover:bg-gray-50 transition-colors ${
                  !notification.read ? "bg-purple-50/30" : ""
                }`}
              >
                <div className="flex items-start gap-4">
                  <div className={`p-3 ${notification.bgColor} rounded-xl`}>
                    <Icon className={`w-6 h-6 ${notification.iconColor}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-1">
                      <h3 className="font-semibold text-gray-900">{notification.title}</h3>
                      <div className="flex items-center gap-2">
                        {!notification.read && (
                          <span className="w-2 h-2 bg-purple-600 rounded-full"></span>
                        )}
                        <button className="p-1 hover:bg-gray-100 rounded transition-colors">
                          <X className="w-4 h-4 text-gray-500" />
                        </button>
                      </div>
                    </div>
                    <p className="text-gray-600 mb-2">{notification.message}</p>
                    <p className="text-sm text-gray-500">{notification.time}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
