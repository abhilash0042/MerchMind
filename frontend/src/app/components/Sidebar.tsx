import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  TrendingUp,
  Users,
  Settings,
  BarChart3,
  HelpCircle,
  Database,
  Brain,
  Wallet,
} from "lucide-react";
import { NavLink } from "react-router";
import { useSidebar } from "../layouts/SidebarContext";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: BarChart3, label: "Analytics", path: "/analytics" },
  { icon: ShoppingCart, label: "Orders", path: "/orders" },
  { icon: Package, label: "Inventory", path: "/inventory" },
  { icon: TrendingUp, label: "Revenue", path: "/revenue" },
  { icon: Users, label: "Customers", path: "/customers" },
  { icon: Database, label: "Data Import", path: "/import" },
  { icon: Brain, label: "AI Intelligence", path: "/ai/intelligence" },
  { icon: Wallet, label: "Payments", path: "/payments" },
];

const bottomItems = [
  { icon: Settings, label: "Settings", path: "/settings" },
  { icon: HelpCircle, label: "Help", path: "/help" },
];

export function Sidebar() {
  const { isCollapsed } = useSidebar();

  return (
    <aside
      className={`bg-white dark:bg-neutral-900 border-r border-gray-200 dark:border-neutral-800 flex flex-col h-screen fixed left-0 top-0 z-30 transition-all duration-300 ease-in-out select-none ${
        isCollapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Logo Header */}
      <div
        className={`p-4 border-b border-gray-200 dark:border-neutral-800 flex items-center min-h-[73px] ${
          isCollapsed ? "justify-center" : "gap-3"
        }`}
      >
        <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center shadow-md shadow-purple-500/20 flex-shrink-0">
          <BarChart3 className="w-5 h-5 text-white" />
        </div>
        {!isCollapsed && (
          <span className="text-xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent truncate">
            CommercePulse
          </span>
        )}
      </div>

      {/* Scrollable Navigation */}
      <nav className="flex-1 overflow-y-auto min-h-0 py-3 px-2 space-y-1 sidebar-scrollbar overflow-x-hidden">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `w-full flex items-center rounded-xl transition-all duration-150 group relative ${
                  isCollapsed ? "justify-center h-10 px-0" : "gap-3 px-3.5 py-2.5"
                } ${
                  isActive
                    ? "bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 font-medium"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-neutral-800/80 hover:text-gray-900 dark:hover:text-gray-100"
                }`
              }
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-105" />
              {!isCollapsed && (
                <span className="font-medium text-sm truncate">{item.label}</span>
              )}
              {isCollapsed && (
                <div className="absolute left-full ml-3 px-3 py-1.5 bg-gray-900 dark:bg-neutral-800 text-white text-xs font-medium rounded-lg shadow-xl whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-150 transform translate-x-1 group-hover:translate-x-0 z-50 border border-gray-800 dark:border-neutral-700">
                  {item.label}
                </div>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Navigation */}
      <div className="p-2 border-t border-gray-200 dark:border-neutral-800 space-y-1 flex-shrink-0">
        {bottomItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `w-full flex items-center rounded-xl transition-all duration-150 group relative ${
                  isCollapsed ? "justify-center h-10 px-0" : "gap-3 px-3.5 py-2.5"
                } ${
                  isActive
                    ? "bg-purple-50 dark:bg-purple-950/60 text-purple-600 dark:text-purple-400 font-medium"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-neutral-800/80 hover:text-gray-900 dark:hover:text-gray-100"
                }`
              }
              title={isCollapsed ? item.label : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-105" />
              {!isCollapsed && (
                <span className="font-medium text-sm truncate">{item.label}</span>
              )}
              {isCollapsed && (
                <div className="absolute left-full ml-3 px-3 py-1.5 bg-gray-900 dark:bg-neutral-800 text-white text-xs font-medium rounded-lg shadow-xl whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-150 transform translate-x-1 group-hover:translate-x-0 z-50 border border-gray-800 dark:border-neutral-700">
                  {item.label}
                </div>
              )}
            </NavLink>
          );
        })}
      </div>
    </aside>
  );
}