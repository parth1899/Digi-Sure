import React from "react";
import {
  UserCog,
  Shield,
  ClipboardList,
  Wallet,
  FolderLock,
  Users,
  HeadphonesIcon,
  Lock,
  Gift,
} from "lucide-react";

interface NavItem {
  id: string;
  icon: React.ElementType;
  label: string;
}

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const navItems: NavItem[] = [
  { id: "personal", icon: UserCog, label: "Personal Information" },
  { id: "policies", icon: Shield, label: "Insurance Policies" },
  { id: "claims", icon: ClipboardList, label: "Claims Management" },
  { id: "payments", icon: Wallet, label: "Payments & Billing" },
  { id: "documents", icon: FolderLock, label: "Documents Vault" },
  { id: "nominees", icon: Users, label: "Nominees" },
  { id: "support", icon: HeadphonesIcon, label: "Support" },
  { id: "security", icon: Lock, label: "Security Settings" },
  { id: "rewards", icon: Gift, label: "Rewards & Referrals" },
];

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <div className="w-full md:w-64 space-y-1">
      {navItems.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          onClick={() => setActiveTab(id)}
          className={`w-full flex items-center space-x-3 px-4 py-3 text-sm font-medium rounded-lg ${
            activeTab === id
              ? "bg-blue-50 text-blue-700"
              : "text-gray-700 hover:bg-gray-50"
          }`}
        >
          <Icon className="w-5 h-5" />
          <span>{label}</span>
        </button>
      ))}
    </div>
  );
};

export default Sidebar;
