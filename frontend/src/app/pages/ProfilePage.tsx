import { User, Mail, Phone, MapPin, Calendar, Briefcase, Award, TrendingUp } from "lucide-react";
import { ImageWithFallback } from "../components/figma/ImageWithFallback";

export function ProfilePage() {
  return (
    <>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900">My Profile</h1>
        <p className="text-gray-600 mt-2">View and manage your profile information</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Card */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl p-8 shadow-sm text-center">
            <div className="w-32 h-32 mx-auto bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-4xl font-semibold mb-6">
              BB
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Founder</h2>
            <p className="text-gray-600 mb-6">Brew Boulevard</p>
            
            <div className="space-y-4 text-left">
              <div className="flex items-center gap-3 text-gray-600">
                <Mail className="w-5 h-5" />
                <span className="text-sm">founder@brewboulevard.com</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Phone className="w-5 h-5" />
                <span className="text-sm">+91 98765 43210</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <MapPin className="w-5 h-5" />
                <span className="text-sm">Bengaluru, India</span>
              </div>
              <div className="flex items-center gap-3 text-gray-600">
                <Calendar className="w-5 h-5" />
                <span className="text-sm">Joined March 2024</span>
              </div>
            </div>

            <button className="w-full mt-6 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-medium transition-colors">
              Edit Profile
            </button>
          </div>

          {/* Quick Stats */}
          <div className="bg-white rounded-2xl p-6 shadow-sm mt-6">
            <h3 className="font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total Revenue</span>
                <span className="font-semibold text-gray-900">₹14,825,000</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Orders</span>
                <span className="font-semibold text-gray-900">1,680</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Customers</span>
                <span className="font-semibold text-gray-900">2,847</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Products</span>
                <span className="font-semibold text-gray-900">124</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* About */}
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">About</h2>
            <p className="text-gray-600 leading-relaxed mb-6">
              E-commerce analytics specialist with 5+ years of experience in data-driven decision making. 
              Passionate about helping businesses grow through actionable insights and strategic planning. 
              Currently managing a multi-million dollar e-commerce operation with a focus on customer experience 
              and sustainable growth.
            </p>
            
            <div className="grid grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-1">Company</p>
                <p className="font-semibold text-gray-900">Brew Boulevard</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Department</p>
                <p className="font-semibold text-gray-900">Executive</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Role</p>
                <p className="font-semibold text-gray-900">Founder & CEO</p>
              </div>
              <div>
                <p className="text-sm text-gray-600 mb-1">Experience</p>
                <p className="font-semibold text-gray-900">5+ years</p>
              </div>
            </div>
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Achievements</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-6 bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl border border-amber-200">
                <div className="w-12 h-12 bg-amber-500 rounded-xl flex items-center justify-center mb-4">
                  <Award className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Revenue Milestone</h3>
                <p className="text-sm text-gray-600">Reached ₹10M in annual revenue</p>
              </div>

              <div className="p-6 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
                <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Growth Expert</h3>
                <p className="text-sm text-gray-600">Achieved 120% YoY growth</p>
              </div>

              <div className="p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center mb-4">
                  <User className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Customer Champion</h3>
                <p className="text-sm text-gray-600">4.9/5 average customer rating</p>
              </div>

              <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center mb-4">
                  <Briefcase className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Early Adopter</h3>
                <p className="text-sm text-gray-600">Using CommercePulse since Day 1</p>
              </div>
            </div>
          </div>

          {/* Activity Timeline */}
          <div className="bg-white rounded-2xl p-8 shadow-sm">
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">Recent Activity</h2>
            <div className="space-y-6">
              {[
                {
                  action: "Updated inventory for 3 products",
                  time: "2 hours ago",
                  color: "bg-blue-500",
                },
                {
                  action: "Processed 12 new orders",
                  time: "5 hours ago",
                  color: "bg-green-500",
                },
                {
                  action: "Generated weekly sales report",
                  time: "1 day ago",
                  color: "bg-purple-500",
                },
                {
                  action: "Added new product: Artisan Cold Brew Concentrate",
                  time: "2 days ago",
                  color: "bg-amber-500",
                },
              ].map((activity, idx) => (
                <div key={idx} className="flex items-start gap-4">
                  <div className={`w-3 h-3 ${activity.color} rounded-full mt-1`}></div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{activity.action}</p>
                    <p className="text-sm text-gray-600">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
