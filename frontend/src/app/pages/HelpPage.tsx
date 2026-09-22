import {
  Book,
  MessageCircle,
  HelpCircle,
  FileText,
  Video,
  Mail,
  Search,
  ExternalLink,
} from "lucide-react";

const faqs = [
  {
    question: "How do I track my inventory levels?",
    answer: "Navigate to the Inventory page from the sidebar. You'll see real-time stock levels, low stock alerts, and can manually adjust quantities.",
  },
  {
    question: "Can I export my sales data?",
    answer: "Yes! Go to the Revenue or Analytics page and click the 'Export' button in the top right. You can export data in CSV or PDF format.",
  },
  {
    question: "How are AI insights generated?",
    answer: "Our AI analyzes your historical data, market trends, and customer behavior to provide actionable recommendations for pricing, inventory, and marketing.",
  },
  {
    question: "What payment methods do you accept?",
    answer: "We accept all major credit cards (Visa, Mastercard, Amex) and support billing through Stripe for secure payment processing.",
  },
];

const resources = [
  {
    icon: Book,
    title: "Documentation",
    description: "Comprehensive guides and API references",
    link: "#",
    color: "bg-blue-500",
  },
  {
    icon: Video,
    title: "Video Tutorials",
    description: "Step-by-step video guides for all features",
    link: "#",
    color: "bg-purple-500",
  },
  {
    icon: FileText,
    title: "Knowledge Base",
    description: "Articles and best practices",
    link: "#",
    color: "bg-green-500",
  },
  {
    icon: MessageCircle,
    title: "Community Forum",
    description: "Connect with other users",
    link: "#",
    color: "bg-amber-500",
  },
];

export function HelpPage() {
  return (
    <>
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-semibold text-gray-900 mb-2">Help Center</h1>
        <p className="text-gray-600">Find answers and get support</p>
      </div>

      {/* Search */}
      <div className="max-w-2xl mx-auto mb-12">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search for help articles, guides, and FAQs..."
            className="w-full pl-12 pr-4 py-4 border-2 border-gray-200 rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-lg"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <button className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all text-left group">
          <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <MessageCircle className="w-6 h-6 text-purple-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Chat with Support</h3>
          <p className="text-sm text-gray-600">Get instant help from our support team</p>
        </button>

        <button className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all text-left group">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Mail className="w-6 h-6 text-blue-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Email Support</h3>
          <p className="text-sm text-gray-600">Send us a detailed message</p>
        </button>

        <button className="bg-white rounded-2xl p-8 shadow-sm hover:shadow-md transition-all text-left group">
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
            <Video className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-semibold text-gray-900 mb-2">Schedule a Call</h3>
          <p className="text-sm text-gray-600">Book a session with our team</p>
        </button>
      </div>

      {/* Resources */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Resources</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {resources.map((resource, idx) => {
            const Icon = resource.icon;
            return (
              <a
                key={idx}
                href={resource.link}
                className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-all group"
              >
                <div
                  className={`w-12 h-12 ${resource.color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
                >
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                  {resource.title}
                  <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                </h3>
                <p className="text-sm text-gray-600">{resource.description}</p>
              </a>
            );
          })}
        </div>
      </div>

      {/* FAQs */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Frequently Asked Questions</h2>
        <div className="space-y-6">
          {faqs.map((faq, idx) => (
            <div key={idx} className="pb-6 border-b border-gray-200 last:border-0">
              <div className="flex items-start gap-3">
                <HelpCircle className="w-5 h-5 text-purple-600 mt-1 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">{faq.question}</h3>
                  <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 text-center">
          <p className="text-gray-600 mb-4">Still have questions?</p>
          <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors">
            Contact Support Team
          </button>
        </div>
      </div>
    </>
  );
}
