import { useState } from "react";
import { Sparkles, X, Send, Minimize2, Maximize2 } from "lucide-react";

const sampleQuestions = [
  "What's my revenue trend?",
  "Show low stock items",
  "Top selling products",
  "Customer satisfaction rate",
];

const aiResponses = [
  {
    question: "What's my revenue trend?",
    answer: "Your revenue has grown by 12.5% this month, reaching $148,250. The trend shows steady growth with a strong performance in Electronics and Fashion categories. I recommend maintaining current inventory levels for these categories.",
  },
  {
    question: "Show low stock items",
    answer: "You have 118 items with low stock levels. The most critical are: Yoga Mat Premium (38 units), Running Shoes Elite (15 units), and Smart Watch Series 5 (89 units). I suggest reordering these items soon to avoid stockouts.",
  },
  {
    question: "Top selling products",
    answer: "Your top 3 selling products are: 1) Wireless Headphones Pro (245 units), 2) Smart Watch Series 5 (89 units), 3) Bluetooth Speaker (198 units). These items contribute to 35% of your total revenue.",
  },
  {
    question: "Customer satisfaction rate",
    answer: "Your current customer satisfaction rate is 94.2%, which is excellent! Return rate is at 7.4%, slightly above the 5% target. Consider reviewing product descriptions for the Electronics category to reduce returns.",
  },
];

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Array<{ type: "user" | "ai"; text: string }>>([
    {
      type: "ai",
      text: "👋 Hi! I'm your AI assistant. I can help you analyze your data, answer questions about your business, and provide insights. Try asking me something!",
    },
  ]);
  const [inputValue, setInputValue] = useState("");

  const handleQuestionClick = (question: string) => {
    const response = aiResponses.find((r) => r.question === question);
    
    setMessages((prev) => [
      ...prev,
      { type: "user", text: question },
      { type: "ai", text: response?.answer || "Let me analyze that for you..." },
    ]);
  };

  const handleSend = () => {
    if (!inputValue.trim()) return;

    setMessages((prev) => [
      ...prev,
      { type: "user", text: inputValue },
      {
        type: "ai",
        text: "I'm analyzing your request. This is a demo response. In a production environment, I would provide detailed insights based on your actual data.",
      },
    ]);
    setInputValue("");
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center group z-50"
      >
        <Sparkles className="w-6 h-6 text-white group-hover:scale-110 transition-transform" />
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
      </button>
    );
  }

  return (
    <div
      className={`fixed bottom-6 right-6 bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50 transition-all ${
        isMinimized ? "w-80 h-16" : "w-96 h-[600px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">AI Assistant</h3>
            <p className="text-xs text-green-600">● Online</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isMinimized ? (
              <Maximize2 className="w-4 h-4 text-gray-600" />
            ) : (
              <Minimize2 className="w-4 h-4 text-gray-600" />
            )}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-4 h-4 text-gray-600" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    message.type === "user"
                      ? "bg-purple-600 text-white"
                      : "bg-gray-100 text-gray-900"
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}

            {/* Quick Questions */}
            {messages.length === 1 && (
              <div className="space-y-2">
                <p className="text-xs text-gray-600 px-2">Quick questions:</p>
                {sampleQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuestionClick(question)}
                    className="w-full text-left px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-xl text-sm text-purple-700 transition-colors"
                  >
                    {question}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask me anything..."
                className="flex-1 px-4 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition-all"
              />
              <button
                onClick={handleSend}
                className="p-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
