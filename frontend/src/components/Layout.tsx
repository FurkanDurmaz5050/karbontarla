import { useState } from "react";
import { Outlet, NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../App";
import {
  LayoutDashboard,
  Map,
  Activity,
  FileText,
  ShoppingCart,
  LogOut,
  Sprout,
  Menu,
  X,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/fields", icon: Map, label: "Tarlalarım" },
  { to: "/sensors", icon: Activity, label: "Sensörler" },
  { to: "/reports", icon: FileText, label: "Raporlar" },
  { to: "/marketplace", icon: ShoppingCart, label: "Pazar" },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const currentLabel = navItems.find(
    (item) => item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to)
  )?.label || "KarbonTarla";

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-karbon-700 text-white flex flex-col transform transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-6 border-b border-karbon-600 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sprout className="w-8 h-8 text-karbon-300" />
            <div>
              <h1 className="text-lg font-bold">KarbonTarla</h1>
              <p className="text-xs text-karbon-300">Tarladan, Karbon Borsasına</p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 text-karbon-300 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-karbon-600 text-white font-semibold"
                    : "text-karbon-200 hover:bg-karbon-600/50"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-karbon-600">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-karbon-400 rounded-full flex items-center justify-center text-sm font-bold">
              {user?.full_name?.charAt(0) || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name || "Kullanıcı"}</p>
              <p className="text-xs text-karbon-300 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-sm text-karbon-300 hover:text-white transition-colors w-full"
          >
            <LogOut className="w-4 h-4" />
            Çıkış Yap
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto w-full">
        {/* Mobile header */}
        <div className="sticky top-0 z-30 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 lg:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1.5 rounded-lg hover:bg-gray-100"
          >
            <Menu className="w-5 h-5 text-gray-700" />
          </button>
          <div className="flex items-center gap-2">
            <Sprout className="w-5 h-5 text-karbon-600" />
            <span className="font-semibold text-gray-800">{currentLabel}</span>
          </div>
        </div>
        <div className="p-4 md:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
