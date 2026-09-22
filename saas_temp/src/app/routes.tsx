import { createBrowserRouter } from "react-router";
import { RootLayout } from "./layouts/RootLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { OrdersPage } from "./pages/OrdersPage";
import { InventoryPage } from "./pages/InventoryPage";
import { RevenuePage } from "./pages/RevenuePage";
import { CustomersPage } from "./pages/CustomersPage";
import { ProductDetailPage } from "./pages/ProductDetailPage";
import { SettingsPage } from "./pages/SettingsPage";
import { NotificationsPage } from "./pages/NotificationsPage";
import { ProfilePage } from "./pages/ProfilePage";
import { HelpPage } from "./pages/HelpPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: RootLayout,
    children: [
      { index: true, Component: DashboardPage },
      { path: "analytics", Component: AnalyticsPage },
      { path: "orders", Component: OrdersPage },
      { path: "inventory", Component: InventoryPage },
      { path: "revenue", Component: RevenuePage },
      { path: "customers", Component: CustomersPage },
      { path: "products/:id", Component: ProductDetailPage },
      { path: "settings", Component: SettingsPage },
      { path: "notifications", Component: NotificationsPage },
      { path: "profile", Component: ProfilePage },
      { path: "help", Component: HelpPage },
    ],
  },
]);