import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import {
  LayoutDashboard,
  Map,
  Activity,
  FileText,
  ShoppingCart,
  LogOut,
  Sprout,
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

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-karbon-700 text-white flex flex-col">
        <div className="p-6 border-b border-karbon-600">
          <div className="flex items-center gap-3">
            <Sprout className="w-8 h-8 text-karbon-300" />
            <div>
              <h1 className="text-lg font-bold">KarbonTarla</h1>
              <p className="text-xs text-karbon-300">Tarladan, Karbon Borsasına</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
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
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
