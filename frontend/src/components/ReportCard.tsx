import { FileText, Download, Calendar } from "lucide-react";

interface Report {
  id: string;
  report_type: string;
  period_start: string;
  period_end: string;
  generated_at: string;
  pdf_path: string | null;
}

interface Props {
  report: Report;
  onDownload: () => void;
}

const typeLabels: Record<string, string> = {
  monitoring: "İzleme Raporu",
  verification: "Doğrulama Raporu",
  baseline: "Temel Çizgi Raporu",
};

export default function ReportCard({ report, onDownload }: Props) {
  return (
    <div className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-blue-50 rounded-lg flex items-center justify-center">
          <FileText className="w-5 h-5 text-blue-500" />
        </div>
        <div>
          <p className="font-medium text-gray-800">
            {typeLabels[report.report_type] || report.report_type}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-400 mt-1">
            <Calendar className="w-3 h-3" />
            <span>
              {new Date(report.period_start).toLocaleDateString("tr-TR")} –{" "}
              {new Date(report.period_end).toLocaleDateString("tr-TR")}
            </span>
            <span className="text-gray-300">•</span>
            <span>
              {new Date(report.generated_at).toLocaleDateString("tr-TR")}
            </span>
          </div>
        </div>
      </div>
      <button
        onClick={onDownload}
        className="flex items-center gap-1 text-sm text-karbon-600 hover:text-karbon-700 font-medium"
      >
        <Download className="w-4 h-4" />
        İndir
      </button>
    </div>
  );
}
