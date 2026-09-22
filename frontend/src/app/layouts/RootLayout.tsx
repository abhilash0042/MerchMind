import { Sidebar } from "../components/Sidebar";
import { Header } from "../components/Header";
import { Outlet } from "react-router";

export function RootLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      <div className="flex-1 ml-64">
        <Header />
        <main className="p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
