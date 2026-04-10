import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { carbonAPI, fieldsAPI } from "../api/client";
import CarbonBalanceCard from "../components/CarbonBalanceCard";
import { Map, TrendingUp, FileText, ShoppingCart, Plus, Loader2 } from "lucide-react";

interface CarbonSummary {
  total_credits: number;
  total_tradeable: number;
  total_value_usd: number;
  credits_by_status: Record<string, number>;
  fields_count: number;
}

interface FieldData {
  id: string;
  name: string;
  area_ha: number;
  soil_type: string | null;
  current_practice: string | null;
  status: string;
}

export default function Dashboard() {
  const [summary, setSummary] = useState<CarbonSummary | null>(null);
  const [fields, setFields] = useState<FieldData[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([
      carbonAPI.getSummary().catch(() => ({ data: null })),
      fieldsAPI.list().catch(() => ({ data: [] })),
    ]).then(([summaryRes, fieldsRes]) => {
      setSummary(summaryRes.data);
      setFields(fieldsRes.data || []);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-karbon-500" />
      </div>
    );
  }

  const usdToTry = 38.5;
  const totalTRY = (summary?.total_value_usd || 0) * usdToTry;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
          <p className="text-gray-500 text-sm">Karbon kredi özetiniz ve tarla durumunuz</p>
        </div>
        <button
          onClick={() => navigate("/fields")}
          className="bg-karbon-600 hover:bg-karbon-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors w-full sm:w-auto"
        >
          <Plus className="w-4 h-4" />
          Tarla Ekle
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <CarbonBalanceCard
          title="Toplam Karbon Geliri"
          value={`₺${totalTRY.toLocaleString("tr-TR", { maximumFractionDigits: 0 })}`}
          subtitle={`$${(summary?.total_value_usd || 0).toLocaleString("en-US", { maximumFractionDigits: 0 })}`}
          icon={TrendingUp}
          color="green"
        />
        <CarbonBalanceCard
          title="Toplam CO₂ Kredisi"
          value={`${(summary?.total_tradeable || 0).toFixed(1)} ton`}
          subtitle="Satışa uygun"
          icon={TrendingUp}
          color="blue"
        />
        <CarbonBalanceCard
          title="Kayıtlı Tarla"
          value={`${summary?.fields_count || fields.length}`}
          subtitle="Aktif izleme"
          icon={Map}
          color="purple"
        />
        <CarbonBalanceCard
          title="Doğrulama Durumu"
          value={`${summary?.credits_by_status?.verified || 0}`}
          subtitle="Onaylı kredi"
          icon={FileText}
          color="orange"
        />
      </div>

      {/* Fields List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800">Tarlalarım</h2>
        </div>
        {fields.length === 0 ? (
          <div className="p-12 text-center text-gray-500">
            <Map className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="font-medium">Henüz tarla eklenmemiş</p>
            <p className="text-sm mt-1">İlk tarlanızı eklemek için "Tarlalarım" sayfasına gidin</p>
            <button
              onClick={() => navigate("/fields")}
              className="mt-4 bg-karbon-50 text-karbon-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-karbon-100 transition-colors"
            >
              Tarla Ekle
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {fields.map((field) => (
              <div
                key={field.id}
                className="p-4 hover:bg-gray-50 transition-colors cursor-pointer flex items-center justify-between"
                onClick={() => navigate("/fields")}
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-karbon-50 rounded-lg flex items-center justify-center">
                    <Map className="w-5 h-5 text-karbon-600" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{field.name}</p>
                    <p className="text-sm text-gray-500">
                      {field.area_ha} ha • {field.soil_type || "—"} • {field.current_practice || "—"}
                    </p>
                  </div>
                </div>
                <span
                  className={`text-xs px-3 py-1 rounded-full font-medium ${
                    field.status === "active"
                      ? "bg-green-50 text-green-700"
                      : "bg-gray-100 text-gray-600"
                  }`}
                >
                  {field.status === "active" ? "Aktif" : field.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => navigate("/marketplace")}
          className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-left group"
        >
          <ShoppingCart className="w-8 h-8 text-karbon-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-800">Kredi Sat</h3>
          <p className="text-sm text-gray-500 mt-1">Karbon kredilerinizi pazara çıkarın</p>
        </button>
        <button
          onClick={() => navigate("/reports")}
          className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-left group"
        >
          <FileText className="w-8 h-8 text-blue-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-800">Rapor Oluştur</h3>
          <p className="text-sm text-gray-500 mt-1">Verra uyumlu MRV raporu indirin</p>
        </button>
        <button
          onClick={() => navigate("/sensors")}
          className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow text-left group"
        >
          <TrendingUp className="w-8 h-8 text-purple-500 mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-800">Sensör Verileri</h3>
          <p className="text-sm text-gray-500 mt-1">IoT sensör okumalarını inceleyin</p>
        </button>
      </div>
    </div>
  );
}
