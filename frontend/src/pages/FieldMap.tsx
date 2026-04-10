import { useEffect, useState, useCallback } from "react";
import { fieldsAPI, satelliteAPI } from "../api/client";
import NDVIMap from "../components/NDVIMap";
import SensorChart from "../components/SensorChart";
import { Plus, Loader2, Trash2, Eye, MapPin, X, Undo2 } from "lucide-react";

interface FieldData {
  id: string;
  name: string;
  area_ha: number;
  soil_type: string | null;
  current_practice: string | null;
  status: string;
  geometry_geojson: any;
}

interface NDVIData {
  field_id: string;
  series: Array<{ date: string; ndvi: number; cloud_cover: number | null }>;
  stats: {
    mean_ndvi: number;
    trend: string;
    health_score: number;
    total_observations: number;
  };
}

export default function FieldMap() {
  const [fields, setFields] = useState<FieldData[]>([]);
  const [selectedField, setSelectedField] = useState<FieldData | null>(null);
  const [ndviData, setNdviData] = useState<NDVIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [drawMode, setDrawMode] = useState(false);
  const [drawPoints, setDrawPoints] = useState<[number, number][]>([]);
  const [formData, setFormData] = useState({
    name: "",
    soil_type: "Balçıklı",
    current_practice: "no_till",
  });

  useEffect(() => {
    loadFields();
  }, []);

  const loadFields = async () => {
    setLoading(true);
    try {
      const res = await fieldsAPI.list();
      setFields(res.data || []);
    } catch {
      setFields([]);
    }
    setLoading(false);
  };

  const handleSelectField = async (field: FieldData) => {
    setSelectedField(field);
    setNdviData(null);
    try {
      const res = await satelliteAPI.getNDVI(field.id, 12);
      setNdviData(res.data);
    } catch {
      // NDVI verisi yok
    }
  };

  const handleMapClick = useCallback((lat: number, lng: number) => {
    setDrawPoints((prev) => [...prev, [lat, lng]]);
  }, []);

  const handleCreateField = async (e: React.FormEvent) => {
    e.preventDefault();
    if (drawPoints.length < 3) {
      alert("Haritada en az 3 köşe noktası seçmelisiniz");
      return;
    }
    try {
      // GeoJSON uses [lng, lat] order — close the polygon
      const coords = drawPoints.map((p) => [p[1], p[0]]);
      coords.push(coords[0]); // close ring
      await fieldsAPI.create({
        name: formData.name,
        geometry: { type: "Polygon", coordinates: [coords] },
        soil_type: formData.soil_type,
        current_practice: formData.current_practice,
      });
      setShowForm(false);
      setDrawMode(false);
      setDrawPoints([]);
      setFormData({ name: "", soil_type: "Balçıklı", current_practice: "no_till" });
      loadFields();
    } catch (err: any) {
      alert(err.response?.data?.detail || "Tarla oluşturulurken hata oluştu");
    }
  };

  const handleDeleteField = async (fieldId: string) => {
    if (!confirm("Bu tarlayı silmek istediğinizden emin misiniz?")) return;
    try {
      await fieldsAPI.delete(fieldId);
      setSelectedField(null);
      setNdviData(null);
      loadFields();
    } catch {
      alert("Silme hatası");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-karbon-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Tarlalarım</h1>
          <p className="text-gray-500 text-sm">Tarla yönetimi ve uydu analizi</p>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setDrawMode(!showForm); setDrawPoints([]); setSelectedField(null); }}
          className="bg-karbon-600 hover:bg-karbon-700 text-white px-4 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium w-full sm:w-auto"
        >
          {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          {showForm ? "İptal" : "Yeni Tarla"}
        </button>
      </div>

      {/* New field form */}
      {showForm && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-karbon-600" />
            Haritadan Tarla Çiz
          </h3>
          <form onSubmit={handleCreateField} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="text"
                placeholder="Tarla adı"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="px-3 py-2 border rounded-lg"
                required
              />
              <select
                value={formData.soil_type}
                onChange={(e) => setFormData({ ...formData, soil_type: e.target.value })}
                className="px-3 py-2 border rounded-lg"
              >
                <option value="Killi">Killi</option>
                <option value="Kumlu">Kumlu</option>
                <option value="Balçıklı">Balçıklı</option>
                <option value="Tınlı">Tınlı</option>
                <option value="Organik">Organik</option>
              </select>
              <select
                value={formData.current_practice}
                onChange={(e) => setFormData({ ...formData, current_practice: e.target.value })}
                className="px-3 py-2 border rounded-lg"
              >
                <option value="no_till">Sürümsüz Tarım</option>
                <option value="reduced_till">Az Sürüm</option>
                <option value="conventional">Konvansiyonel</option>
                <option value="cover_crop">Kapak Bitkisi</option>
                <option value="composting">Kompostlama</option>
              </select>
            </div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-3 flex-wrap">
                <span className="text-sm text-gray-500">
                  Seçilen köşe: <span className="font-bold text-karbon-700">{drawPoints.length}</span>
                  {drawPoints.length < 3 && <span className="text-orange-500 ml-1">(en az 3 gerekli)</span>}
                </span>
                {drawPoints.length > 0 && (
                  <button type="button" onClick={() => setDrawPoints((p) => p.slice(0, -1))} className="text-xs text-gray-500 hover:text-red-500 flex items-center gap-1">
                    <Undo2 className="w-3 h-3" /> Son noktayı sil
                  </button>
                )}
              </div>
              <div className="flex gap-2 w-full sm:w-auto">
                <button type="submit" disabled={drawPoints.length < 3} className="bg-karbon-600 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-40 flex-1 sm:flex-none">Kaydet</button>
                <button type="button" onClick={() => { setShowForm(false); setDrawMode(false); setDrawPoints([]); }} className="bg-gray-200 px-4 py-2 rounded-lg flex-1 sm:flex-none">İptal</button>
              </div>
            </div>
          </form>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Field list */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-700">{fields.length} Tarla</h3>
          </div>
          <div className="max-h-[600px] overflow-y-auto divide-y divide-gray-50">
            {fields.map((field) => (
              <div
                key={field.id}
                className={`p-4 cursor-pointer transition-colors ${
                  selectedField?.id === field.id ? "bg-karbon-50" : "hover:bg-gray-50"
                }`}
                onClick={() => handleSelectField(field)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-800">{field.name}</p>
                    <p className="text-sm text-gray-500">
                      {field.area_ha} ha • {field.soil_type}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleSelectField(field); }}
                      className="p-1.5 hover:bg-gray-100 rounded"
                    >
                      <Eye className="w-4 h-4 text-gray-400" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteField(field.id); }}
                      className="p-1.5 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
            {fields.length === 0 && (
              <div className="p-8 text-center text-gray-400 text-sm">
                Henüz tarla kaydı yok
              </div>
            )}
          </div>
        </div>

        {/* Map and NDVI */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 h-[300px] md:h-[400px]">
            <NDVIMap
              fieldPolygon={selectedField?.geometry_geojson}
              ndviValue={ndviData?.stats?.mean_ndvi}
              onMapClick={handleMapClick}
              drawMode={drawMode}
              drawPoints={drawPoints}
            />
          </div>

          {ndviData && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-800 mb-3">NDVI Analizi — {selectedField?.name}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-karbon-600">{ndviData.stats.mean_ndvi?.toFixed(3)}</p>
                  <p className="text-xs text-gray-500">Ortalama NDVI</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{ndviData.stats.health_score}</p>
                  <p className="text-xs text-gray-500">Sağlık Skoru</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{ndviData.stats.trend}</p>
                  <p className="text-xs text-gray-500">Trend</p>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <p className="text-2xl font-bold text-gray-600">{ndviData.stats.total_observations}</p>
                  <p className="text-xs text-gray-500">Gözlem</p>
                </div>
              </div>
              <SensorChart
                data={ndviData.series.map((s) => ({
                  date: s.date,
                  value: s.ndvi,
                  label: "NDVI",
                }))}
                title="NDVI Zaman Serisi"
                color="#2d6a4f"
                unit=""
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
