import { useEffect, useState } from "react";
import { fieldsAPI, carbonAPI, reportsAPI } from "../api/client";
import ReportCard from "../components/ReportCard";
import { FileText, Loader2, Calculator, Download } from "lucide-react";

interface FieldData {
  id: string;
  name: string;
  area_ha: number;
}

interface CreditData {
  id: string;
  field_id: string;
  vintage_year: number | null;
  credit_tons: number | null;
  tradeable_tons: number | null;
  verification_status: string;
}

interface ReportData {
  id: string;
  field_id: string;
  credit_id: string | null;
  report_type: string;
  period_start: string;
  period_end: string;
  pdf_path: string | null;
  generated_at: string;
}

export default function CarbonReport() {
  const [fields, setFields] = useState<FieldData[]>([]);
  const [credits, setCredits] = useState<CreditData[]>([]);
  const [reports, setReports] = useState<ReportData[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedField, setSelectedField] = useState("");
  const [calcYear, setCalcYear] = useState(new Date().getFullYear());

  useEffect(() => {
    Promise.all([
      fieldsAPI.list().catch(() => ({ data: [] })),
      carbonAPI.listCredits().catch(() => ({ data: [] })),
    ]).then(([fieldsRes, creditsRes]) => {
      setFields(fieldsRes.data || []);
      setCredits(creditsRes.data || []);
      if (fieldsRes.data?.length > 0) {
        setSelectedField(fieldsRes.data[0].id);
        loadFieldReports(fieldsRes.data[0].id);
      }
      setLoading(false);
    });
  }, []);

  const loadFieldReports = async (fieldId: string) => {
    try {
      const res = await reportsAPI.listByField(fieldId);
      setReports(res.data || []);
    } catch {
      setReports([]);
    }
  };

  const handleCalculate = async () => {
    if (!selectedField) return;
    setCalculating(true);
    try {
      const res = await carbonAPI.calculate({
        field_id: selectedField,
        year: calcYear,
      });
      alert(
        `Hesaplama tamamlandı!\n\nSatışa uygun kredi: ${res.data.tradeable_tons} ton CO₂e\nMetodoloji: VM0042`
      );
      const creditsRes = await carbonAPI.listCredits();
      setCredits(creditsRes.data || []);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Hesaplama hatası");
    }
    setCalculating(false);
  };

  const handleGenerateReport = async () => {
    if (!selectedField) return;
    setGenerating(true);
    const fieldCredits = credits.filter((c) => c.field_id === selectedField);
    try {
      const res = await reportsAPI.generate({
        field_id: selectedField,
        credit_id: fieldCredits.length > 0 ? fieldCredits[0].id : null,
        report_type: "monitoring",
        period_start: `${calcYear}-01-01`,
        period_end: `${calcYear}-12-31`,
        include_satellite_maps: true,
        methodology: "VM0042",
      });
      alert("Rapor oluşturuldu!");
      setReports((prev) => [res.data, ...prev]);
    } catch (err: any) {
      alert(err.response?.data?.detail || "Rapor oluşturma hatası");
    }
    setGenerating(false);
  };

  const handleDownload = async (reportId: string) => {
    try {
      const res = await reportsAPI.download(reportId);
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.download = `MRV_Report_${reportId}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch {
      alert("İndirme hatası");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-karbon-500" />
      </div>
    );
  }

  const fieldCredits = credits.filter((c) => c.field_id === selectedField);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Karbon Raporları</h1>
        <p className="text-gray-500">Verra VM0042 karbon hesaplama ve MRV rapor üretimi</p>
      </div>

      {/* Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Tarla</label>
            <select
              value={selectedField}
              onChange={(e) => {
                setSelectedField(e.target.value);
                loadFieldReports(e.target.value);
              }}
              className="px-3 py-2 border rounded-lg min-w-[200px]"
            >
              {fields.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.area_ha} ha)
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Yıl</label>
            <input
              type="number"
              value={calcYear}
              onChange={(e) => setCalcYear(parseInt(e.target.value))}
              className="px-3 py-2 border rounded-lg w-24"
              min={2020}
              max={2030}
            />
          </div>
          <button
            onClick={handleCalculate}
            disabled={calculating || !selectedField}
            className="bg-karbon-600 hover:bg-karbon-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium disabled:opacity-50"
          >
            {calculating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
            Karbon Hesapla
          </button>
          <button
            onClick={handleGenerateReport}
            disabled={generating || !selectedField}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 text-sm font-medium disabled:opacity-50"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
            MRV Raporu Oluştur
          </button>
        </div>
      </div>

      {/* Credits */}
      {fieldCredits.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100">
          <div className="p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-800">Karbon Kredileri</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="text-left p-3 font-medium text-gray-600">Yıl</th>
                  <th className="text-left p-3 font-medium text-gray-600">Kredi (ton)</th>
                  <th className="text-left p-3 font-medium text-gray-600">Satışa Uygun</th>
                  <th className="text-left p-3 font-medium text-gray-600">Durum</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {fieldCredits.map((credit) => (
                  <tr key={credit.id} className="hover:bg-gray-50">
                    <td className="p-3">{credit.vintage_year || "—"}</td>
                    <td className="p-3 font-medium">{credit.credit_tons?.toFixed(2)} ton CO₂e</td>
                    <td className="p-3 text-karbon-600 font-semibold">
                      {credit.tradeable_tons?.toFixed(2)} ton CO₂e
                    </td>
                    <td className="p-3">
                      <span
                        className={`text-xs px-2 py-1 rounded-full font-medium ${
                          credit.verification_status === "verified"
                            ? "bg-green-50 text-green-700"
                            : credit.verification_status === "pending"
                            ? "bg-yellow-50 text-yellow-700"
                            : "bg-red-50 text-red-700"
                        }`}
                      >
                        {credit.verification_status === "verified"
                          ? "Doğrulanmış"
                          : credit.verification_status === "pending"
                          ? "Beklemede"
                          : credit.verification_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Reports */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100">
        <div className="p-5 border-b border-gray-100">
          <h2 className="font-semibold text-gray-800">Oluşturulan Raporlar</h2>
        </div>
        {reports.length === 0 ? (
          <div className="p-12 text-center text-gray-400">
            <FileText className="w-10 h-10 mx-auto mb-2" />
            <p>Henüz rapor oluşturulmamış</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-50">
            {reports.map((report) => (
              <ReportCard
                key={report.id}
                report={report}
                onDownload={() => handleDownload(report.id)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
