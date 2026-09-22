import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  TrendingUp,
  Users,
  Settings,
  BarChart3,
  HelpCircle,
} from "lucide-react";
import { NavLink } from "react-router";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/" },
  { icon: BarChart3, label: "Analytics", path: "/analytics" },
  { icon: ShoppingCart, label: "Orders", path: "/orders" },
  { icon: Package, label: "Inventory", path: "/inventory" },
  { icon: TrendingUp, label: "Revenue", path: "/revenue" },
  { icon: Users, label: "Customers", path: "/customers" },
];

const bottomItems = [
  { icon: Settings, label: "Settings", path: "/settings" },
  { icon: HelpCircle, label: "Help", path: "/help" },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg flex items-center justify-center">
            <BarChart3 className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold text-gray-900">
            CommercePulse
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? "bg-purple-50 text-purple-600"
                    : "text-gray-600 hover:bg-gray-50"
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Navigation */}
      <div className="p-4 space-y-1 border-t border-gray-200">
        {bottomItems.map((item, index) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={index}
              to={item.path}
              className={({ isActive }) =>
                `w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? "bg-purple-50 text-purple-600"
                    : "text-gray-600 hover:bg-gray-50"
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </NavLink>
          );
        })}
      </div>
    </aside>
  );
}