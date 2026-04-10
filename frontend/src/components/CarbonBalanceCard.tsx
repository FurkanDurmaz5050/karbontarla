import { LucideIcon } from "lucide-react";

interface Props {
  title: string;
  value: string;
  subtitle?: string;
  icon: LucideIcon;
  color: "green" | "blue" | "purple" | "orange" | "red";
}

const colorMap = {
  green: { bg: "bg-green-50", text: "text-green-600", icon: "text-green-500" },
  blue: { bg: "bg-blue-50", text: "text-blue-600", icon: "text-blue-500" },
  purple: { bg: "bg-purple-50", text: "text-purple-600", icon: "text-purple-500" },
  orange: { bg: "bg-orange-50", text: "text-orange-600", icon: "text-orange-500" },
  red: { bg: "bg-red-50", text: "text-red-600", icon: "text-red-500" },
};

export default function CarbonBalanceCard({ title, value, subtitle, icon: Icon, color }: Props) {
  const c = colorMap[color];
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500 font-medium">{title}</span>
        <div className={`w-9 h-9 ${c.bg} rounded-lg flex items-center justify-center`}>
          <Icon className={`w-5 h-5 ${c.icon}`} />
        </div>
      </div>
      <p className={`text-2xl font-bold ${c.text}`}>{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-1">{subtitle}</p>}
    </div>
  );
}
