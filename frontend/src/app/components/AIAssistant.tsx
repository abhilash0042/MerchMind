import { useState, useRef, useEffect } from "react";
import { Sparkles, X, Send, Minimize2, Maximize2, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ensureSeller, apiClient } from "../services/api";

const sampleQuestions = [
  "What's my revenue by marketplace?",
  "Show me my top selling products",
  "Are there any low stock items?",
  "What is my overall ROAS?",
  "How is payments reconciliation looking?",
];

export function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [contextData, setContextData] = useState<any>(null);
  
  const [messages, setMessages] = useState<Array<{ type: "user" | "ai" | "system"; text: string }>>([
    {
      type: "ai",
      text: "👋 Hi! I'm your Brew Boulevard AI Business Analyst. Ask me about revenue, products, inventory, ads/ROAS, logistics, customers, payments, or any SKU — I'll pull live numbers.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch real business context when opened
  useEffect(() => {
    if (isOpen && !contextData) {
      loadContext();
    }
  }, [isOpen]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const loadContext = async () => {
    try {
      const sellerId = await ensureSeller();
      const dashboard = await apiClient.get(`/analytics/dashboard/summary?seller_id=${sellerId}&days=30`);
      setContextData(dashboard);
    } catch (err) {
      console.error("Failed to load AI context:", err);
    }
  };

  const callGroqAPI = async (userMessage: string, chatHistory: any[]) => {
    const sellerId = await ensureSeller();
    
    // Inject dynamic routing context
    const currentPath = window.location.pathname;
    let productId = 'None';
    if (currentPath.includes('/ai/products/')) {
        productId = currentPath.split('/').pop() || 'None';
    }

    const payload = {
      message: userMessage,
      history: chatHistory.filter(m => m.type !== 'system'),
      context: {
          ...contextData,
          current_page: currentPath,
          product_id: productId
      }
    };

    const response = await apiClient.post(`/ai/chat?seller_id=${sellerId}`, payload);
    return response.reply;
  };

  const handleSend = async (text: string = inputValue) => {
    if (!text.trim() || isLoading) return;

    const userMsg = text.trim();
    setInputValue("");
    
    // Add user message immediately
    setMessages((prev) => [...prev, { type: "user", text: userMsg }]);
    setIsLoading(true);

    try {
      const aiResponse = await callGroqAPI(userMsg, messages);
      setMessages((prev) => [...prev, { type: "ai", text: aiResponse }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { 
        type: "system", 
        text: "Sorry, I encountered an error connecting to the intelligence engine. Please try again." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-full shadow-[0_0_20px_rgba(147,51,234,0.4)] hover:shadow-[0_0_30px_rgba(147,51,234,0.6)] transition-all flex items-center justify-center group z-50 border border-purple-400/30"
      >
        <Sparkles className="w-6 h-6 text-white group-hover:scale-110 transition-transform" />
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-[#0a0a1a]"></span>
      </button>
    );
  }

  return (
    <div
      className={`fixed bottom-6 right-6 bg-[#0a0a1a]/95 backdrop-blur-xl rounded-2xl shadow-[0_0_40px_rgba(0,0,0,0.5)] border border-purple-500/20 flex flex-col z-50 transition-all duration-300 ${
        isMinimized ? "w-80 h-[72px]" : "w-96 h-[600px]"
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5 rounded-t-2xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-inner border border-white/10">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-white leading-tight">AI Strategist</h3>
            <p className="text-[10px] text-emerald-400 font-mono tracking-wider flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> ONLINE
            </p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-white"
          >
            {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors text-white/60 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-purple-500/20 scrollbar-track-transparent">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                    message.type === "user"
                      ? "bg-purple-600 text-white rounded-tr-sm"
                      : message.type === "system"
                      ? "bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs"
                      : "bg-white/10 text-gray-100 border border-white/5 rounded-tl-sm prose prose-invert prose-sm max-w-none"
                  }`}
                >
                  {message.type === "ai" ? (
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
                      p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2 last:mb-0" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2 last:mb-0" {...props} />,
                      li: ({node, ...props}) => <li className="mb-1" {...props} />
                    }}>
                      {message.text}
                    </ReactMarkdown>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
                  )}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] rounded-2xl rounded-tl-sm px-4 py-3 bg-white/5 border border-white/5 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                  <span className="text-sm text-purple-400/70">Analyzing data...</span>
                </div>
              </div>
            )}

            {/* Quick Questions (only show at start) */}
            {messages.length === 1 && !isLoading && (
              <div className="space-y-2 mt-6">
                <p className="text-[10px] uppercase tracking-wider font-bold text-white/40 px-2">Suggested queries</p>
                <div className="flex flex-col gap-2">
                  {sampleQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSend(question)}
                      className="w-full text-left px-4 py-2.5 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20 hover:border-purple-500/40 rounded-xl text-sm text-purple-300 transition-all duration-200"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/10 bg-white/5 rounded-b-2xl">
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                disabled={isLoading}
                placeholder={isLoading ? "Please wait..." : "Ask your business analyst..."}
                className="flex-1 px-4 py-3 bg-[#0a0a1a] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all disabled:opacity-50 placeholder:text-white/30"
              />
              <button
                onClick={() => handleSend()}
                disabled={isLoading || !inputValue.trim()}
                className="p-3 bg-purple-600 text-white rounded-xl hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:hover:bg-purple-600 shadow-lg"
              >
                <Send className="w-5 h-5 ml-0.5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
