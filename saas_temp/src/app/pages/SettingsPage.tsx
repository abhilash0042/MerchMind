import { useState } from "react";
import {
  User,
  Bell,
  Lock,
  CreditCard,
  Users,
  Globe,
  Palette,
  Database,
  Smartphone,
  Mail,
  Shield,
  Key,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

const tabs = [
  { id: "profile", label: "Profile", icon: User },
  { id: "account", label: "Account", icon: Lock },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "billing", label: "Billing", icon: CreditCard },
  { id: "team", label: "Team", icon: Users },
  { id: "integrations", label: "Integrations", icon: Globe },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "security", label: "Security", icon: Shield },
];

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");

  return (
    <>
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <div className="lg:col-span-1">
          <nav className="bg-white rounded-2xl p-4 shadow-sm space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                    activeTab === tab.id
                      ? "bg-purple-50 text-purple-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3">
          {activeTab === "profile" && <ProfileTab />}
          {activeTab === "account" && <AccountTab />}
          {activeTab === "notifications" && <NotificationsTab />}
          {activeTab === "billing" && <BillingTab />}
          {activeTab === "team" && <TeamTab />}
          {activeTab === "integrations" && <IntegrationsTab />}
          {activeTab === "appearance" && <AppearanceTab />}
          {activeTab === "security" && <SecurityTab />}
        </div>
      </div>
    </>
  );
}

function ProfileTab() {
  return (
    <div className="bg-white rounded-2xl p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Profile Information</h2>

      <div className="space-y-6">
        {/* Profile Photo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Profile Photo</label>
          <div className="flex items-center gap-4">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-semibold">
              JD
            </div>
            <div>
              <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-medium transition-colors">
                Upload Photo
              </button>
              <p className="text-xs text-gray-500 mt-1">JPG, PNG or GIF. Max size 2MB.</p>
            </div>
          </div>
        </div>

        {/* Name Fields */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
            <input
              type="text"
              defaultValue="John"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
            <input
              type="text"
              defaultValue="Doe"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
          <input
            type="email"
            defaultValue="john.doe@commercepulse.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Phone */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
          <input
            type="tel"
            defaultValue="+1 (555) 123-4567"
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Bio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
          <textarea
            rows={4}
            defaultValue="E-commerce analytics specialist with 5+ years of experience in data-driven decision making."
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-3 pt-4">
          <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
            Cancel
          </button>
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}

function AccountTab() {
  return (
    <div className="space-y-6">
      {/* Change Password */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Change Password</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
            <input
              type="password"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
            <input
              type="password"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
            <input
              type="password"
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Update Password
          </button>
        </div>
      </div>

      {/* Delete Account */}
      <div className="bg-white rounded-2xl p-8 shadow-sm border-2 border-red-100">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Delete Account</h2>
        <p className="text-gray-600 mb-6">
          Once you delete your account, there is no going back. Please be certain.
        </p>
        <button className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors">
          Delete Account
        </button>
      </div>
    </div>
  );
}

function NotificationsTab() {
  return (
    <div className="bg-white rounded-2xl p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>

      <div className="space-y-6">
        {/* Email Notifications */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-purple-600" />
            Email Notifications
          </h3>
          <div className="space-y-3 ml-7">
            <NotificationToggle label="Order updates" description="Notifications about new orders and fulfillment" />
            <NotificationToggle label="Inventory alerts" description="Low stock and out of stock alerts" />
            <NotificationToggle label="Revenue reports" description="Daily and weekly revenue summaries" />
            <NotificationToggle label="Marketing emails" description="Tips, promotions, and product updates" />
          </div>
        </div>

        {/* Push Notifications */}
        <div>
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Smartphone className="w-5 h-5 text-purple-600" />
            Push Notifications
          </h3>
          <div className="space-y-3 ml-7">
            <NotificationToggle label="Critical alerts" description="Urgent issues requiring immediate attention" />
            <NotificationToggle label="Customer messages" description="New customer inquiries and support tickets" />
            <NotificationToggle label="System updates" description="Platform updates and maintenance notices" />
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Save Preferences
          </button>
        </div>
      </div>
    </div>
  );
}

function NotificationToggle({ label, description }: { label: string; description: string }) {
  const [enabled, setEnabled] = useState(true);
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="font-medium text-gray-900">{label}</p>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      <button
        onClick={() => setEnabled(!enabled)}
        className={`relative w-12 h-6 rounded-full transition-colors ${
          enabled ? "bg-purple-600" : "bg-gray-300"
        }`}
      >
        <span
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
            enabled ? "translate-x-6" : ""
          }`}
        />
      </button>
    </div>
  );
}

function BillingTab() {
  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-8 border border-purple-200">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Pro Plan</h2>
            <p className="text-gray-600">Your current subscription</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-semibold text-gray-900">$99</p>
            <p className="text-sm text-gray-600">per month</p>
          </div>
        </div>
        <div className="flex gap-3">
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Upgrade Plan
          </button>
          <button className="px-6 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 font-medium transition-colors">
            Cancel Subscription
          </button>
        </div>
      </div>

      {/* Payment Method */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Payment Method</h2>
        <div className="flex items-center justify-between p-6 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <CreditCard className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="font-semibold text-gray-900">•••• •••• •••• 4242</p>
              <p className="text-sm text-gray-600">Expires 12/2026</p>
            </div>
          </div>
          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
            Update
          </button>
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Billing History</h2>
        <div className="space-y-3">
          {[
            { date: "Mar 1, 2026", amount: "$99.00", status: "Paid" },
            { date: "Feb 1, 2026", amount: "$99.00", status: "Paid" },
            { date: "Jan 1, 2026", amount: "$99.00", status: "Paid" },
          ].map((invoice, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{invoice.date}</p>
                  <p className="text-sm text-gray-600">{invoice.amount}</p>
                </div>
              </div>
              <button className="text-purple-600 hover:text-purple-700 font-medium text-sm">
                Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TeamTab() {
  const teamMembers = [
    { name: "John Doe", email: "john.doe@company.com", role: "Owner", avatar: "JD" },
    { name: "Sarah Smith", email: "sarah.smith@company.com", role: "Admin", avatar: "SS" },
    { name: "Mike Johnson", email: "mike.johnson@company.com", role: "Member", avatar: "MJ" },
  ];

  return (
    <div className="bg-white rounded-2xl p-8 shadow-sm">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-semibold text-gray-900">Team Members</h2>
          <p className="text-gray-600 mt-1">Manage your team and permissions</p>
        </div>
        <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
          Invite Member
        </button>
      </div>

      <div className="space-y-3">
        {teamMembers.map((member, idx) => (
          <div key={idx} className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                {member.avatar}
              </div>
              <div>
                <p className="font-semibold text-gray-900">{member.name}</p>
                <p className="text-sm text-gray-600">{member.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <select className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500">
                <option>Owner</option>
                <option>Admin</option>
                <option>Member</option>
              </select>
              <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                Remove
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function IntegrationsTab() {
  const integrations = [
    { name: "Shopify", description: "E-commerce platform integration", connected: true, icon: "🛍️" },
    { name: "Stripe", description: "Payment processing", connected: true, icon: "💳" },
    { name: "Slack", description: "Team communication", connected: false, icon: "💬" },
    { name: "Mailchimp", description: "Email marketing", connected: false, icon: "📧" },
  ];

  return (
    <div className="bg-white rounded-2xl p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Integrations</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {integrations.map((integration, idx) => (
          <div key={idx} className="p-6 border-2 border-gray-200 rounded-xl hover:border-purple-300 transition-colors">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-3xl">{integration.icon}</span>
                <div>
                  <h3 className="font-semibold text-gray-900">{integration.name}</h3>
                  <p className="text-sm text-gray-600">{integration.description}</p>
                </div>
              </div>
            </div>
            {integration.connected ? (
              <button className="w-full py-2 bg-green-50 text-green-700 rounded-lg font-medium border border-green-200">
                Connected
              </button>
            ) : (
              <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
                Connect
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function AppearanceTab() {
  return (
    <div className="bg-white rounded-2xl p-8 shadow-sm">
      <h2 className="text-2xl font-semibold text-gray-900 mb-6">Appearance</h2>

      <div className="space-y-6">
        {/* Theme Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Theme</label>
          <div className="grid grid-cols-3 gap-4">
            <button className="p-6 border-2 border-purple-500 rounded-xl bg-purple-50">
              <div className="w-full h-20 bg-white rounded-lg mb-3"></div>
              <p className="font-medium text-gray-900">Light</p>
            </button>
            <button className="p-6 border-2 border-gray-200 rounded-xl hover:border-purple-300 transition-colors">
              <div className="w-full h-20 bg-gray-900 rounded-lg mb-3"></div>
              <p className="font-medium text-gray-900">Dark</p>
            </button>
            <button className="p-6 border-2 border-gray-200 rounded-xl hover:border-purple-300 transition-colors">
              <div className="w-full h-20 bg-gradient-to-r from-white to-gray-900 rounded-lg mb-3"></div>
              <p className="font-medium text-gray-900">Auto</p>
            </button>
          </div>
        </div>

        {/* Accent Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">Accent Color</label>
          <div className="flex gap-3">
            {["bg-purple-600", "bg-blue-600", "bg-green-600", "bg-red-600", "bg-orange-600"].map((color, idx) => (
              <button
                key={idx}
                className={`w-12 h-12 ${color} rounded-lg border-2 ${
                  idx === 0 ? "border-gray-900" : "border-transparent"
                } hover:scale-110 transition-transform`}
              />
            ))}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-4">
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}

function SecurityTab() {
  return (
    <div className="space-y-6">
      {/* Two-Factor Authentication */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">Two-Factor Authentication</h2>
            <p className="text-gray-600">Add an extra layer of security to your account</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Enabled</span>
          </div>
        </div>
        <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors">
          Configure 2FA
        </button>
      </div>

      {/* API Keys */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-2">API Keys</h2>
            <p className="text-gray-600">Manage your API keys for integrations</p>
          </div>
          <button className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors">
            Generate New Key
          </button>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
            <div className="flex items-center gap-3">
              <Key className="w-5 h-5 text-gray-600" />
              <div>
                <p className="font-medium text-gray-900">Production Key</p>
                <p className="text-sm text-gray-600 font-mono">sk_live_••••••••••••4242</p>
              </div>
            </div>
            <button className="text-red-600 hover:text-red-700 font-medium text-sm">
              Revoke
            </button>
          </div>
        </div>
      </div>

      {/* Active Sessions */}
      <div className="bg-white rounded-2xl p-8 shadow-sm">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Active Sessions</h2>
        <div className="space-y-3">
          {[
            { device: "MacBook Pro", location: "San Francisco, CA", time: "Active now" },
            { device: "iPhone 14 Pro", location: "San Francisco, CA", time: "2 hours ago" },
          ].map((session, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 hover:bg-gray-50 rounded-xl transition-colors">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">{session.device}</p>
                  <p className="text-sm text-gray-600">{session.location} • {session.time}</p>
                </div>
              </div>
              <button className="text-red-600 hover:text-red-700 font-medium text-sm">
                Revoke
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
