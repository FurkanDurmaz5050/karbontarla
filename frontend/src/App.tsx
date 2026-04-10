import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect, createContext, useContext } from "react";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import FieldMap from "./pages/FieldMap";
import SensorData from "./pages/SensorData";
import CarbonReport from "./pages/CarbonReport";
import Marketplace from "./pages/Marketplace";
import Layout from "./components/Layout";
import { apiClient } from "./api/client";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  token: null,
  login: () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("access_token")
  );

  useEffect(() => {
    if (token) {
      apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      apiClient
        .get("/api/v1/auth/me")
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem("access_token");
          setToken(null);
        });
    }
  }, [token]);

  const login = (accessToken: string, refreshToken: string, userData: User) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
    setToken(accessToken);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete apiClient.defaults.headers.common["Authorization"];
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={token ? <Navigate to="/" /> : <Login />} />
          <Route
            element={token ? <Layout /> : <Navigate to="/login" />}
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/fields" element={<FieldMap />} />
            <Route path="/sensors" element={<SensorData />} />
            <Route path="/reports" element={<CarbonReport />} />
            <Route path="/marketplace" element={<Marketplace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}

export default App;
