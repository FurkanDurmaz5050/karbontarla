import { useEffect, useState } from "react";
import { sensorsAPI } from "../api/client";
import SensorChart from "../components/SensorChart";
import { Activity, Loader2, Thermometer, Droplets, Gauge } from "lucide-react";

interface SensorInfo {
  id: string;
  field_id: string;
  sensor_external_id: string;
  sensor_type: string;
  name: string | null;
  status: string;
}

interface Reading {
  id: string;
  timestamp: string;
  soil_moisture: number | null;
  soil_temp_c: number | null;
  soil_ph: number | null;
  organic_matter: number | null;
  co2_flux: number | null;
  battery_pct: number | null;
}

export default function SensorData() {
  const [sensors, setSensors] = useState<SensorInfo[]>([]);
  const [selectedSensor, setSelectedSensor] = useState<SensorInfo | null>(null);
  const [readings, setReadings] = useState<Reading[]>([]);
  const [latestReading, setLatestReading] = useState<Reading | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    sensorsAPI
      .list()
      .then((res) => setSensors(res.data || []))
      .catch(() => setSensors([]))
      .finally(() => setLoading(false));
  }, []);

  const handleSelectSensor = async (sensor: SensorInfo) => {
    setSelectedSensor(sensor);
    try {
      const [readingsRes, latestRes] = await Promise.all([
        sensorsAPI.getReadings(sensor.id, 30),
        sensorsAPI.getLatest(sensor.id),
      ]);
      setReadings(readingsRes.data || []);
      setLatestReading(latestRes.data);
    } catch {
      setReadings([]);
      setLatestReading(null);
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
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Sensör Verileri</h1>
        <p className="text-gray-500">IoT toprak sensörlerinden canlı veriler</p>
      </div>

      {sensors.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
          <Activity className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="font-medium text-gray-600">Henüz sensör kaydı yok</p>
          <p className="text-sm text-gray-400 mt-1">
            IoT sensörlerinizi kaydedin veya MQTT ile bağlanın
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sensor List */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100">
            <div className="p-4 border-b border-gray-100">
              <h3 className="font-semibold text-gray-700">{sensors.length} Sensör</h3>
            </div>
            <div className="divide-y divide-gray-50">
              {sensors.map((sensor) => (
                <div
                  key={sensor.id}
                  onClick={() => handleSelectSensor(sensor)}
                  className={`p-4 cursor-pointer ${
                    selectedSensor?.id === sensor.id ? "bg-karbon-50" : "hover:bg-gray-50"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        sensor.status === "active" ? "bg-green-500" : "bg-gray-300"
                      }`}
                    />
                    <div>
                      <p className="font-medium text-sm text-gray-800">
                        {sensor.name || sensor.sensor_external_id}
                      </p>
                      <p className="text-xs text-gray-400">{sensor.sensor_type}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Sensor Detail */}
          <div className="lg:col-span-3 space-y-4">
            {selectedSensor ? (
              <>
                {latestReading && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Droplets className="w-4 h-4 text-blue-500" />
                        <span className="text-xs text-gray-500">Nem</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-600">
                        {latestReading.soil_moisture?.toFixed(1) || "—"}%
                      </p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Thermometer className="w-4 h-4 text-red-500" />
                        <span className="text-xs text-gray-500">Sıcaklık</span>
                      </div>
                      <p className="text-2xl font-bold text-red-600">
                        {latestReading.soil_temp_c?.toFixed(1) || "—"}°C
                      </p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Gauge className="w-4 h-4 text-green-500" />
                        <span className="text-xs text-gray-500">pH</span>
                      </div>
                      <p className="text-2xl font-bold text-green-600">
                        {latestReading.soil_ph?.toFixed(1) || "—"}
                      </p>
                    </div>
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Activity className="w-4 h-4 text-purple-500" />
                        <span className="text-xs text-gray-500">CO₂ Fluks</span>
                      </div>
                      <p className="text-2xl font-bold text-purple-600">
                        {latestReading.co2_flux?.toFixed(2) || "—"}
                      </p>
                    </div>
                  </div>
                )}

                {readings.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                      <SensorChart
                        data={readings
                          .filter((r) => r.soil_moisture !== null)
                          .map((r) => ({
                            date: r.timestamp,
                            value: r.soil_moisture!,
                            label: "Nem",
                          }))}
                        title="Toprak Nemi (%)"
                        color="#3b82f6"
                        unit="%"
                      />
                    </div>
                    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                      <SensorChart
                        data={readings
                          .filter((r) => r.co2_flux !== null)
                          .map((r) => ({
                            date: r.timestamp,
                            value: r.co2_flux!,
                            label: "CO₂ Fluks",
                          }))}
                        title="CO₂ Fluks (µmol/m²/s)"
                        color="#8b5cf6"
                        unit=""
                      />
                    </div>
                  </div>
                )}

                {readings.length === 0 && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center text-gray-400">
                    Bu sensörden henüz veri gelmemiş
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center text-gray-400">
                <Activity className="w-8 h-8 mx-auto mb-2" />
                Bir sensör seçin
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
