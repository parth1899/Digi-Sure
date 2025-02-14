import React from "react";
import { ChevronRight, Shield } from "lucide-react";
import { User } from "../../types";

interface PersonalInfoProps {
  user: User;
}

const PersonalInfo: React.FC<PersonalInfoProps> = ({ user }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm text-gray-600">Full Name</label>
            <p className="text-gray-900 font-medium">{user.name}</p>
          </div>
          <div>
            <label className="block text-sm text-gray-600">Customer ID</label>
            <p className="text-gray-900 font-medium">{user.customerId}</p>
          </div>
          <div>
            <label className="block text-sm text-gray-600">Email Address</label>
            <p className="text-gray-900 font-medium">{user.email}</p>
          </div>
          <div>
            <label className="block text-sm text-gray-600">Phone Number</label>
            <p className="text-gray-900 font-medium">{user.phone}</p>
          </div>
          <div className="col-span-2">
            <label className="block text-sm text-gray-600">Address</label>
            <p className="text-gray-900 font-medium">{user.address}</p>
          </div>
        </div>
        <button className="mt-4 text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center">
          Edit Profile <ChevronRight className="w-4 h-4 ml-1" />
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-4">
          Active Insurance Policies
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">
                Life Insurance
              </span>
              <Shield className="w-5 h-5 text-green-600" />
            </div>
            <p className="text-lg font-semibold">₹50,00,000</p>
            <p className="text-sm text-gray-500">Policy: LI-2024-001</p>
          </div>
          {/* Similar blocks for Health and Vehicle insurance */}
        </div>
      </div>
    </div>
  );
};

export default PersonalInfo;
