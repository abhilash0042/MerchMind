import { Search, Bell, User, Settings, LogOut, X, TrendingUp, Package, ShoppingCart } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router";

export function Header() {
  const [showSearch, setShowSearch] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  // Mock search results
  const searchResults = searchQuery.length > 0 ? [
    { type: "Product", name: "Artisan Cold Brew Concentrate", path: "/products/1" },
    { type: "Page", name: "Analytics Dashboard", path: "/analytics" },
    { type: "Page", name: "Inventory Management", path: "/inventory" },
    { type: "Customer", name: "Rahul Sharma", path: "/customers" },
  ].filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  ) : [];

  const notifications = [
    { id: 1, title: "Low Stock Alert", message: "Single-Origin Espresso Roast - 12 units left", time: "5m ago", unread: true },
    { id: 2, title: "Order Fulfilled", message: "Order #12847 shipped via BlueDart", time: "1h ago", unread: true },
    { id: 3, title: "New Review", message: "5-star review on French Press Blend", time: "3h ago", unread: false },
  ];

  return (
    <header className="bg-white border-b border-gray-200 px-8 py-6 relative">
      <div className="flex items-center justify-between">
        {/* Welcome Message */}
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Welcome back, Founder
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Here's what's happening with Brew Boulevard today
          </p>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search products, orders, customers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setShowSearch(true)}
              className="pl-10 pr-4 py-2 w-80 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
            />
            
            {/* Search Dropdown */}
            {showSearch && searchQuery.length > 0 && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowSearch(false)}></div>
                <div className="absolute top-full mt-2 w-full bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50 max-h-96 overflow-y-auto">
                  {searchResults.length > 0 ? (
                    searchResults.map((result, idx) => (
                      <Link
                        key={idx}
                        to={result.path}
                        onClick={() => {
                          setShowSearch(false);
                          setSearchQuery("");
                        }}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
                      >
                        <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                          {result.type === "Product" && <Package className="w-4 h-4 text-purple-600" />}
                          {result.type === "Page" && <TrendingUp className="w-4 h-4 text-purple-600" />}
                          {result.type === "Customer" && <User className="w-4 h-4 text-purple-600" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">{result.name}</p>
                          <p className="text-xs text-gray-600">{result.type}</p>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="px-4 py-3 text-sm text-gray-600 text-center">
                      No results found for "{searchQuery}"
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Notification Icon */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 hover:bg-gray-50 rounded-xl transition-all"
            >
              <Bell className="w-6 h-6 text-gray-600" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)}></div>
                <div className="absolute right-0 top-full mt-2 w-96 bg-white rounded-xl shadow-lg border border-gray-200 z-50">
                  <div className="flex items-center justify-between p-4 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-900">Notifications</h3>
                    <Link 
                      to="/notifications" 
                      onClick={() => setShowNotifications(false)}
                      className="text-sm text-purple-600 hover:text-purple-700 font-medium"
                    >
                      View All
                    </Link>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className={`p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                          notif.unread ? "bg-purple-50/30" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 text-sm mb-1">{notif.title}</p>
                            <p className="text-sm text-gray-600">{notif.message}</p>
                            <p className="text-xs text-gray-500 mt-1">{notif.time}</p>
                          </div>
                          {notif.unread && (
                            <span className="w-2 h-2 bg-purple-600 rounded-full mt-1"></span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* User Avatar */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-3 pl-4 border-l border-gray-200 hover:opacity-80 transition-opacity"
            >
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">Founder</p>
                <p className="text-xs text-gray-600">Brew Boulevard</p>
              </div>
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                BB
              </div>
            </button>

            {/* Profile Dropdown */}
            {showProfile && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowProfile(false)}></div>
                <div className="absolute right-0 top-full mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                  <Link
                    to="/profile"
                    onClick={() => setShowProfile(false)}
                    className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
                  >
                    <User className="w-5 h-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">My Profile</span>
                  </Link>
                  <Link
                    to="/settings"
                    onClick={() => setShowProfile(false)}
                    className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors"
                  >
                    <Settings className="w-5 h-5 text-gray-600" />
                    <span className="text-sm font-medium text-gray-900">Settings</span>
                  </Link>
                  <div className="border-t border-gray-200 my-2"></div>
                  <button
                    onClick={() => {
                      setShowProfile(false);
                      // Handle logout
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-50 transition-colors text-left"
                  >
                    <LogOut className="w-5 h-5 text-red-600" />
                    <span className="text-sm font-medium text-red-600">Logout</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}