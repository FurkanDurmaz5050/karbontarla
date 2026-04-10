import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import { authAPI } from "../api/client";
import { Sprout, Loader2 } from "lucide-react";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isLogin) {
        const res = await authAPI.login({ email, password });
        login(res.data.access_token, res.data.refresh_token, res.data.user);
      } else {
        await authAPI.register({ email, password, full_name: fullName });
        const res = await authAPI.login({ email, password });
        login(res.data.access_token, res.data.refresh_token, res.data.user);
      }
      navigate("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-karbon-700 to-karbon-800 items-center justify-center p-12">
        <div className="max-w-md text-white">
          <div className="flex items-center gap-3 mb-8">
            <Sprout className="w-12 h-12 text-karbon-300" />
            <h1 className="text-4xl font-bold">KarbonTarla</h1>
          </div>
          <p className="text-xl text-karbon-200 mb-6">
            Tarladan, Karbon Borsasına
          </p>
          <p className="text-karbon-300 leading-relaxed">
            Türk çiftçilerini küresel karbon kredi pazarlarına bağlayan dijital platform.
            IoT sensörler ve uydu görüntüleri ile tarlanızın karbon değerini ölçün,
            Verra sertifikası alın ve karbon kredilerinizi satışa sunun.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-4 text-center">
            <div className="bg-karbon-600/50 rounded-lg p-4">
              <div className="text-2xl font-bold text-karbon-100">🛰️</div>
              <div className="text-xs text-karbon-300 mt-2">Uydu İzleme</div>
            </div>
            <div className="bg-karbon-600/50 rounded-lg p-4">
              <div className="text-2xl font-bold text-karbon-100">📊</div>
              <div className="text-xs text-karbon-300 mt-2">MRV Rapor</div>
            </div>
            <div className="bg-karbon-600/50 rounded-lg p-4">
              <div className="text-2xl font-bold text-karbon-100">💰</div>
              <div className="text-xs text-karbon-300 mt-2">Kredi Satışı</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="lg:hidden flex items-center gap-3 mb-8 justify-center">
            <Sprout className="w-10 h-10 text-karbon-600" />
            <h1 className="text-3xl font-bold text-karbon-700">KarbonTarla</h1>
          </div>

          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            {isLogin ? "Giriş Yap" : "Hesap Oluştur"}
          </h2>
          <p className="text-gray-500 mb-8">
            {isLogin
              ? "Hesabınıza giriş yaparak devam edin"
              : "Yeni bir hesap oluşturun"}
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ad Soyad
                </label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-karbon-400 focus:border-transparent outline-none"
                  placeholder="Ali Yılmaz"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                E-posta
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-karbon-400 focus:border-transparent outline-none"
                placeholder="ali@ciftci.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Şifre
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-karbon-400 focus:border-transparent outline-none"
                placeholder="••••••••"
                minLength={8}
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-karbon-600 hover:bg-karbon-700 text-white font-semibold py-3 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {isLogin ? "Giriş Yap" : "Kayıt Ol"}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            {isLogin ? "Hesabınız yok mu?" : "Zaten hesabınız var mı?"}{" "}
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError("");
              }}
              className="text-karbon-600 font-semibold hover:underline"
            >
              {isLogin ? "Kayıt Olun" : "Giriş Yapın"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
