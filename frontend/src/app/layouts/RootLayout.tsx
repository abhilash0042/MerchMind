import { Sidebar } from "../components/Sidebar";
import { Header } from "../components/Header";
import { Outlet } from "react-router";
import { SidebarProvider, useSidebar } from "./SidebarContext";

function RootLayoutContent() {
  const { isCollapsed } = useSidebar();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-neutral-950 text-gray-900 dark:text-gray-100 flex transition-colors duration-200">
      <Sidebar />
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ease-in-out ${
          isCollapsed ? "ml-20" : "ml-64"
        }`}
      >
        <Header />
        <main className="p-8 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export function RootLayout() {
  return (
    <SidebarProvider>
      <RootLayoutContent />
    </SidebarProvider>
  );
}
