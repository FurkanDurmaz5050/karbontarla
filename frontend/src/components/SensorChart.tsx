import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";

interface DataPoint {
  date: string;
  value: number;
  label: string;
}

interface Props {
  data: DataPoint[];
  title: string;
  color: string;
  unit: string;
}

export default function SensorChart({ data, title, color, unit }: Props) {
  if (data.length === 0) {
    return (
      <div className="text-center text-gray-400 text-sm py-8">
        Veri bulunamadı
      </div>
    );
  }

  const formatted = data.map((d) => ({
    ...d,
    dateShort: new Date(d.date).toLocaleDateString("tr-TR", {
      month: "short",
      day: "numeric",
    }),
  }));

  return (
    <div>
      <h4 className="text-sm font-semibold text-gray-700 mb-3">{title}</h4>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={formatted} margin={{ top: 5, right: 5, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id={`fill-${color}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="dateShort" tick={{ fontSize: 11 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 11 }} stroke="#9ca3af" />
          <Tooltip
            formatter={(value: number) => [
              `${value.toFixed(2)}${unit ? " " + unit : ""}`,
              data[0]?.label || title,
            ]}
            labelFormatter={(label) => `Tarih: ${label}`}
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid #e5e7eb",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            fill={`url(#fill-${color})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
