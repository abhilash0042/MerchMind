import { Sparkles, TrendingUp, AlertCircle, Lightbulb, Zap, Clock } from "lucide-react";
import { useState } from "react";
import { apiClient, ensureSeller } from "../services/api";

export function AIInsights() {
  const [insights, setInsights] = useState<any[]>([]);
  const [quickWins, setQuickWins] = useState<string[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const fetchInsights = async () => {
      setLoading(true);
      setError("");
      try {
        const sellerId = await ensureSeller();
        const today = new Date();
        const lastMonth = new Date();
        lastMonth.setDate(today.getDate() - 30);
        
        const requestBody = {
          seller_id: sellerId,
          time_window_start: lastMonth.toISOString().split('T')[0],
          time_window_end: today.toISOString().split('T')[0],
          snapshot_data: {}
        };

        const response = await apiClient.post("/ai/simulate", requestBody);
        
        if (response.status === "success" && response.executive_plan) {
          const plan = response.executive_plan;
          setSummary(plan.primary_problem_statement);
          setQuickWins(plan.quick_wins || []);
          
          // Map backend actions to UI insight format
          const mappedInsights = (plan.ranked_actions || []).map((action: any) => {
            let type = "info";
            let icon = Lightbulb;
            
            if (action.risk_level?.toLowerCase() === "high" || action.timeframe === "Immediate") {
              type = "warning";
              icon = AlertCircle;
            } else if (action.estimated_impact_percentage > 5 || action.timeframe === "This Week") {
              type = "success";
              icon = TrendingUp;
            }

            return {
              icon: icon,
              title: action.action_name,
              reason: action.reason || "",
              strategy: action.strategy || "",
              description: action.description,
              type: type as "success" | "warning" | "info",
              impact: action.financial_impact_monthly,
              timeframe: action.timeframe || "This Month"
            };
          });
          
          setInsights(mappedInsights.slice(0, 4)); // Show top 4 actions
        } else {
          setError(response.message || "AI agents did not return an executive plan.");
        }
      } catch (err) {
        console.error("Error fetching AI insights:", err);
        setError("Could not generate AI recommendations. Confirm the agents service is running on port 8002.");
      } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm relative min-h-[400px]">
      {loading && (
        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex flex-col items-center justify-center rounded-2xl">
          <div className="relative">
            <div className="absolute inset-0 rounded-full blur-xl bg-purple-500/30 animate-pulse"></div>
            <Sparkles className="w-12 h-12 text-purple-600 animate-bounce relative z-10" />
          </div>
          <p className="mt-4 font-medium text-gray-800">Generating AI Strategy...</p>
          <p className="text-xs text-gray-500 mt-1 max-w-[250px] text-center">
            Usually about 15–30 seconds.
          </p>
        </div>
      )}
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Multi-Agent AI Insights</h3>
          <p className="text-sm text-gray-600">
            Personalized strategic recommendations
          </p>
        </div>
      </div>
      
      {!loading && insights.length === 0 && !error && (
        <button
          type="button"
          onClick={fetchInsights}
          className="w-full mb-4 px-4 py-3 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded-xl"
        >
          Generate strategy
        </button>
      )}

      {!loading && error && insights.length === 0 && (
        <div className="mb-4 p-3 bg-amber-50 rounded-lg border border-amber-100 text-sm text-amber-800">
          {error}
        </div>
      )}

      {summary && (
        <div className="mb-4 p-3 bg-purple-50/50 rounded-lg border border-purple-100 text-sm text-gray-800 italic">
          "{summary}"
        </div>
      )}
      
      {/* Quick Wins Section */}
      {quickWins.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-1.5 mb-2">
            <Zap className="w-4 h-4 text-amber-500" />
            <span className="text-sm font-semibold text-gray-900">Quick Wins (Do Today)</span>
          </div>
          <div className="space-y-1.5">
            {quickWins.map((win, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-gray-700 bg-amber-50 rounded-lg px-3 py-2 border border-amber-100">
                <span className="text-amber-600 font-bold mt-0.5">⚡</span>
                <span>{win}</span>
              </div>
            ))}
          </div>
        </div>
      )}

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
                  <h4 className="font-medium text-gray-900 mb-1 flex items-center gap-2">
                    {insight.title}
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                      insight.timeframe === 'Immediate' ? 'bg-red-100 text-red-700' :
                      insight.timeframe === 'This Week' ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      <Clock className="w-2.5 h-2.5 inline mr-0.5" />{insight.timeframe}
                    </span>
                  </h4>
                  {insight.reason && (
                    <p className="text-xs text-gray-500 mb-1">
                      <span className="font-semibold">Why:</span> {insight.reason}
                    </p>
                  )}
                  <p className="text-sm text-gray-700">
                    {insight.description}
                  </p>
                  {insight.strategy && (
                    <p className="text-xs text-gray-600 mt-1">
                      <span className="font-semibold">How:</span> {insight.strategy}
                    </p>
                  )}
                  {insight.impact > 0 && (
                    <p className="text-xs font-semibold mt-2 text-gray-600">
                      Estimated Monthly Impact: <span className="text-green-600">₹{insight.impact.toLocaleString()}</span>
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
