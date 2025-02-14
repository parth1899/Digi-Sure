import React from "react";
import { Bell, User as UserIcon, LogOut, Building2 } from "lucide-react";
import { User } from "../../types";

interface HeaderProps {
  user: User;
}

const Header: React.FC<HeaderProps> = ({ user }) => {
  return (
    <header className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Building2 className="w-8 h-8 text-blue-700" />
            <span className="ml-2 text-xl font-semibold text-gray-900">
              SBI Insurance
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Bell className="w-6 h-6 text-gray-600 cursor-pointer" />
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-blue-700" />
              </div>
              <span className="text-sm font-medium text-gray-700">
                {user.name}
              </span>
            </div>
            <LogOut className="w-6 h-6 text-gray-600 cursor-pointer" />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
