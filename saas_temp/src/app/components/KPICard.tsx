import { LucideIcon } from "lucide-react";
import { LineChart, Line, ResponsiveContainer } from "recharts";

interface KPICardProps {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative" | "neutral";
  icon: LucideIcon;
  iconColor: string;
  sparklineData: number[];
}

export function KPICard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  iconColor,
  sparklineData,
}: KPICardProps) {
  const changeColor =
    changeType === "positive"
      ? "text-green-600"
      : changeType === "negative"
      ? "text-red-600"
      : "text-gray-600";

  const sparklineColor =
    changeType === "positive"
      ? "#10B981"
      : changeType === "negative"
      ? "#EF4444"
      : "#6B7280";

  const data = sparklineData.map((value, index) => ({ value, index }));

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl ${iconColor}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        <div className="w-20 h-12">
          <ResponsiveContainer width="100%" height={48}>
            <LineChart data={data}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={sparklineColor}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="space-y-1">
        <p className="text-sm text-gray-600">{title}</p>
        <p className="text-3xl font-semibold text-gray-900">{value}</p>
        <p className={`text-sm ${changeColor}`}>{change}</p>
      </div>
    </div>
  );
}