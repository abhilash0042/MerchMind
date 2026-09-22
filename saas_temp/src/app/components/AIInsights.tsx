import { Sparkles, TrendingUp, AlertCircle, Lightbulb } from "lucide-react";

const insights = [
  {
    icon: TrendingUp,
    title: "Revenue Growth Opportunity",
    description:
      "Amazon sales are up 23% this month. Consider increasing inventory for top-performing products.",
    type: "success" as const,
  },
  {
    icon: AlertCircle,
    title: "Inventory Alert",
    description:
      "24 products are out of stock. Restock popular items to avoid lost sales.",
    type: "warning" as const,
  },
  {
    icon: Lightbulb,
    title: "Optimization Tip",
    description:
      "Return rate for 'Electronics' category is 7.8%. Review product descriptions and images to reduce returns.",
    type: "info" as const,
  },
];

export function AIInsights() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">AI Insights</h3>
          <p className="text-sm text-gray-600">
            Personalized recommendations for your business
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {insights.map((insight, index) => {
          const Icon = insight.icon;
          const bgColor =
            insight.type === "success"
              ? "bg-green-50"
              : insight.type === "warning"
              ? "bg-amber-50"
              : "bg-blue-50";
          const iconColor =
            insight.type === "success"
              ? "text-green-600"
              : insight.type === "warning"
              ? "text-amber-600"
              : "text-blue-600";

          return (
            <div
              key={index}
              className={`${bgColor} rounded-xl p-4 border border-gray-100`}
            >
              <div className="flex gap-3">
                <div className={`${iconColor} mt-0.5`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {insight.title}
                  </h4>
                  <p className="text-sm text-gray-700">
                    {insight.description}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
