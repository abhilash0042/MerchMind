import {
  Search,
  Bell,
  User,
  Settings,
  LogOut,
  TrendingUp,
  Package,
  Sun,
  Moon,
  PanelLeft,
} from "lucide-react";
import { useState, useEffect } from "react";
import { Link } from "react-router";
import { useSidebar } from "../layouts/SidebarContext";
import { useTheme } from "next-themes";

export function Header() {
  const { isCollapsed, toggleSidebar } = useSidebar();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  const [showSearch, setShowSearch] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    setMounted(true);
  }, []);

  const isDark = mounted && (resolvedTheme === "dark" || theme === "dark");

  const toggleTheme = () => {
    setTheme(isDark ? "light" : "dark");
  };

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
    <header className="bg-white dark:bg-neutral-900 border-b border-gray-200 dark:border-neutral-800 px-8 py-5 relative transition-colors duration-200">
      <div className="flex items-center justify-between">
        {/* Left: Sidebar Toggle & Welcome Message */}
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSidebar}
            className="p-2 rounded-xl text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-neutral-800 transition-colors"
            title={isCollapsed ? "Expand sidebar (Ctrl+B)" : "Collapse sidebar (Ctrl+B)"}
            aria-label="Toggle sidebar"
          >
            <PanelLeft className="w-5 h-5" />
          </button>

          <div>
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">
              Welcome back, Founder
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
              Here's what's happening with Brew Boulevard today
            </p>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Search products, orders, customers..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => setShowSearch(true)}
              className="pl-10 pr-4 py-2 w-72 lg:w-80 bg-gray-50 dark:bg-neutral-800/80 border border-gray-200 dark:border-neutral-700 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white dark:focus:bg-neutral-800 transition-all"
            />
            
            {/* Search Dropdown */}
            {showSearch && searchQuery.length > 0 && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowSearch(false)}></div>
                <div className="absolute top-full mt-2 w-full bg-white dark:bg-neutral-900 rounded-xl shadow-xl border border-gray-200 dark:border-neutral-800 py-2 z-50 max-h-96 overflow-y-auto">
                  {searchResults.length > 0 ? (
                    searchResults.map((result, idx) => (
                      <Link
                        key={idx}
                        to={result.path}
                        onClick={() => {
                          setShowSearch(false);
                          setSearchQuery("");
                        }}
                        className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors"
                      >
                        <div className="w-8 h-8 bg-purple-100 dark:bg-purple-950/60 rounded-lg flex items-center justify-center flex-shrink-0">
                          {result.type === "Product" && <Package className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
                          {result.type === "Page" && <TrendingUp className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
                          {result.type === "Customer" && <User className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{result.name}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{result.type}</p>
                        </div>
                      </Link>
                    ))
                  ) : (
                    <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                      No results found for "{searchQuery}"
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Theme Toggle Button */}
          {mounted && (
            <button
              onClick={toggleTheme}
              className="p-2.5 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-xl transition-all relative group"
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              aria-label="Toggle theme"
            >
              {isDark ? (
                <Sun className="w-5 h-5 text-amber-400 group-hover:rotate-45 transition-transform duration-300" />
              ) : (
                <Moon className="w-5 h-5 text-purple-600 group-hover:-rotate-12 transition-transform duration-300" />
              )}
            </button>
          )}

          {/* Notification Icon */}
          <div className="relative">
            <button 
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2.5 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-neutral-800 rounded-xl transition-all"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowNotifications(false)}></div>
                <div className="absolute right-0 top-full mt-2 w-96 bg-white dark:bg-neutral-900 rounded-xl shadow-xl border border-gray-200 dark:border-neutral-800 z-50 overflow-hidden">
                  <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-neutral-800">
                    <h3 className="font-semibold text-gray-900 dark:text-white text-sm">Notifications</h3>
                    <Link 
                      to="/notifications" 
                      onClick={() => setShowNotifications(false)}
                      className="text-xs text-purple-600 dark:text-purple-400 hover:underline font-medium"
                    >
                      View All
                    </Link>
                  </div>
                  <div className="max-h-96 overflow-y-auto divide-y divide-gray-100 dark:divide-neutral-800">
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className={`p-4 hover:bg-gray-50 dark:hover:bg-neutral-800/60 transition-colors ${
                          notif.unread ? "bg-purple-50/40 dark:bg-purple-950/20" : ""
                        }`}
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900 dark:text-white text-sm mb-1">{notif.title}</p>
                            <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">{notif.message}</p>
                            <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-1.5">{notif.time}</p>
                          </div>
                          {notif.unread && (
                            <span className="w-2 h-2 bg-purple-600 rounded-full mt-1.5 flex-shrink-0"></span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* User Avatar & Menu */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-3 pl-3 border-l border-gray-200 dark:border-neutral-800 hover:opacity-85 transition-opacity"
            >
              <div className="text-right hidden sm:block">
                <p className="text-sm font-medium text-gray-900 dark:text-white leading-tight">Founder</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Brew Boulevard</p>
              </div>
              <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-sm font-semibold shadow-sm">
                BB
              </div>
            </button>

            {/* Profile Dropdown */}
            {showProfile && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setShowProfile(false)}></div>
                <div className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-neutral-900 rounded-xl shadow-xl border border-gray-200 dark:border-neutral-800 py-1.5 z-50 overflow-hidden">
                  <div className="px-4 py-2.5 border-b border-gray-100 dark:border-neutral-800">
                    <p className="text-xs text-gray-400 dark:text-gray-500">Signed in as</p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">hello@brewboulevard.in</p>
                  </div>
                  <Link
                    to="/profile"
                    onClick={() => setShowProfile(false)}
                    className="flex items-center gap-2.5 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors text-gray-700 dark:text-gray-300"
                  >
                    <User className="w-4 h-4 text-gray-400" />
                    <span className="text-sm">My Profile</span>
                  </Link>
                  <Link
                    to="/settings"
                    onClick={() => setShowProfile(false)}
                    className="flex items-center gap-2.5 px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-neutral-800 transition-colors text-gray-700 dark:text-gray-300"
                  >
                    <Settings className="w-4 h-4 text-gray-400" />
                    <span className="text-sm">Settings</span>
                  </Link>
                  <div className="border-t border-gray-100 dark:border-neutral-800 my-1"></div>
                  <button
                    onClick={() => setShowProfile(false)}
                    className="w-full flex items-center gap-2.5 px-4 py-2.5 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors text-left text-red-600 dark:text-red-400"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm font-medium">Logout</span>
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