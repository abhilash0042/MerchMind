import { type LucideIcon } from "lucide-react";
import { LineChart, Line, ResponsiveContainer, AreaChart, Area } from "recharts";

interface MiniAnalyticsCardProps {
  title: string;
  value: string;
  change: string;
  changeType: "positive" | "negative";
  icon: LucideIcon;
  data: number[];
  chartType?: "line" | "area";
}

export function MiniAnalyticsCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  data,
  chartType = "line",
}: MiniAnalyticsCardProps) {
  const chartData = data.map((value, index) => ({ value, index }));
  const color = changeType === "positive" ? "#8B5CF6" : "#EF4444";

  return (
    <div className="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow border border-gray-100">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${changeType === "positive" ? "bg-purple-50" : "bg-red-50"}`}>
            <Icon className={`w-4 h-4 ${changeType === "positive" ? "text-purple-600" : "text-red-600"}`} />
          </div>
          <div>
            <p className="text-xs text-gray-600">{title}</p>
            <p className="text-xl font-semibold text-gray-900 mt-0.5">{value}</p>
          </div>
        </div>
      </div>
      
      <div className="h-16 mb-2">
        <ResponsiveContainer width="100%" height={64}>
          {chartType === "line" ? (
            <LineChart data={chartData}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          ) : (
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={2}
                fill={`url(#gradient-${title})`}
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>
      
      <p className={`text-xs ${changeType === "positive" ? "text-green-600" : "text-red-600"}`}>
        {change}
      </p>
    </div>
  );
}