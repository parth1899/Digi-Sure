import React, { useState } from "react";
import { Shield, Pencil, Check, X } from "lucide-react";

interface User {
  name: string;
  email: string;
  phone: string;
  customerId: string;
  address: string;
  profilePicture?: string;
  aadharNumber?: string;
  panNumber?: string;
  accountNumber?: string;
  ifscCode?: string;
}

const mockUser: User = {
  name: "John Doe",
  email: "john.doe@example.com",
  phone: "+91 98765 43210",
  customerId: "CUS123456",
  address: "123 Main Street, Bangalore, Karnataka 560001",
  aadharNumber: "1234 5678 9012",
  panNumber: "ABCDE1234F",
  accountNumber: "1234567890",
  ifscCode: "BANK0123456",
};

const PersonalInfo: React.FC = () => {
  const [user, setUser] = useState<User>(mockUser);
  const [editMode, setEditMode] = useState({
    personal: false,
    banking: false,
    address: false,
  });
  const [tempData, setTempData] = useState<User>(user);

  const handleEdit = (section: keyof typeof editMode) => {
    setEditMode((prev) => ({ ...prev, [section]: true }));
    setTempData(user);
  };

  const handleCancel = (section: keyof typeof editMode) => {
    setEditMode((prev) => ({ ...prev, [section]: false }));
    setTempData(user);
  };

  const handleSave = (section: keyof typeof editMode) => {
    setUser(tempData);
    setEditMode((prev) => ({ ...prev, [section]: false }));
  };

  const handleChange = (field: keyof User, value: string) => {
    setTempData((prev) => ({ ...prev, [field]: value }));
  };

  const InputField = ({
    label,
    field,
    value,
    onChange,
  }: {
    label: string;
    field: keyof User;
    value: string;
    onChange: (field: keyof User, value: string) => void;
  }) => (
    <div>
      <label className="block text-sm text-gray-600">{label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(field, e.target.value)}
        className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>
  );

  const DisplayField = ({ label, value }: { label: string; value: string }) => (
    <div>
      <label className="block text-sm text-gray-600">{label}</label>
      <p className="text-gray-900 font-medium">{value}</p>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      {/* User Information Top Section */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-start mb-6">
          <h3 className="text-lg font-semibold">User Information</h3>
          {!editMode.personal ? (
            <button
              onClick={() => handleEdit("personal")}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
            >
              <Pencil className="w-4 h-4 mr-1" />
              Edit
            </button>
          ) : (
            <div className="flex space-x-2">
              <button
                onClick={() => handleSave("personal")}
                className="text-green-600 hover:text-green-700 text-sm font-medium flex items-center"
              >
                <Check className="w-4 h-4 mr-1" />
                Save
              </button>
              <button
                onClick={() => handleCancel("personal")}
                className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center"
              >
                <X className="w-4 h-4 mr-1" />
                Cancel
              </button>
            </div>
          )}
        </div>
        <div className="flex items-start space-x-6">
          <div className="flex-shrink-0">
            <div className="relative">
              <img
                src={
                  user.profilePicture ||
                  "https://images.unsplash.com/photo-1633332755192-727a05c4013d?w=400&h=400&fit=crop"
                }
                alt={user.name}
                className="w-24 h-24 rounded-full object-cover border-2 border-gray-200"
              />
              <button className="absolute bottom-0 right-0 bg-white rounded-full p-1 shadow-md hover:bg-gray-50">
                <Pencil className="w-4 h-4 text-gray-600" />
              </button>
            </div>
          </div>
          <div className="flex-grow grid grid-cols-1 md:grid-cols-2 gap-4">
            {editMode.personal ? (
              <>
                <InputField
                  label="Full Name"
                  field="name"
                  value={tempData.name}
                  onChange={handleChange}
                />
                <InputField
                  label="Email Address"
                  field="email"
                  value={tempData.email}
                  onChange={handleChange}
                />
                <InputField
                  label="Mobile Number"
                  field="phone"
                  value={tempData.phone}
                  onChange={handleChange}
                />
                <DisplayField label="Customer ID" value={user.customerId} />
              </>
            ) : (
              <>
                <DisplayField label="Full Name" value={user.name} />
                <DisplayField label="Email Address" value={user.email} />
                <DisplayField label="Mobile Number" value={user.phone} />
                <DisplayField label="Customer ID" value={user.customerId} />
              </>
            )}
          </div>
        </div>
      </div>

      {/* Banking & Identity Details */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-start mb-6">
          <h3 className="text-lg font-semibold">Banking & Identity Details</h3>
          {!editMode.banking ? (
            <button
              onClick={() => handleEdit("banking")}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
            >
              <Pencil className="w-4 h-4 mr-1" />
              Edit
            </button>
          ) : (
            <div className="flex space-x-2">
              <button
                onClick={() => handleSave("banking")}
                className="text-green-600 hover:text-green-700 text-sm font-medium flex items-center"
              >
                <Check className="w-4 h-4 mr-1" />
                Save
              </button>
              <button
                onClick={() => handleCancel("banking")}
                className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center"
              >
                <X className="w-4 h-4 mr-1" />
                Cancel
              </button>
            </div>
          )}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {editMode.banking ? (
            <>
              <InputField
                label="Aadhar Number"
                field="aadharNumber"
                value={tempData.aadharNumber || ""}
                onChange={handleChange}
              />
              <InputField
                label="PAN Number"
                field="panNumber"
                value={tempData.panNumber || ""}
                onChange={handleChange}
              />
              <InputField
                label="Account Number"
                field="accountNumber"
                value={tempData.accountNumber || ""}
                onChange={handleChange}
              />
              <InputField
                label="IFSC Code"
                field="ifscCode"
                value={tempData.ifscCode || ""}
                onChange={handleChange}
              />
            </>
          ) : (
            <>
              <div>
                <label className="block text-sm text-gray-600">
                  Aadhar Number
                </label>
                <p className="text-gray-900 font-medium">
                  XXXX XXXX {user.aadharNumber?.slice(-4)}
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-600">
                  PAN Number
                </label>
                <p className="text-gray-900 font-medium">
                  XXXXX{user.panNumber?.slice(-5)}
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-600">
                  Account Number
                </label>
                <p className="text-gray-900 font-medium">
                  XXXX XXXX {user.accountNumber?.slice(-4)}
                </p>
              </div>
              <div>
                <label className="block text-sm text-gray-600">IFSC Code</label>
                <p className="text-gray-900 font-medium">{user.ifscCode}</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Address Information */}
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-start mb-4">
          <h3 className="text-lg font-semibold">Address Information</h3>
          {!editMode.address ? (
            <button
              onClick={() => handleEdit("address")}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center"
            >
              <Pencil className="w-4 h-4 mr-1" />
              Edit
            </button>
          ) : (
            <div className="flex space-x-2">
              <button
                onClick={() => handleSave("address")}
                className="text-green-600 hover:text-green-700 text-sm font-medium flex items-center"
              >
                <Check className="w-4 h-4 mr-1" />
                Save
              </button>
              <button
                onClick={() => handleCancel("address")}
                className="text-red-600 hover:text-red-700 text-sm font-medium flex items-center"
              >
                <X className="w-4 h-4 mr-1" />
                Cancel
              </button>
            </div>
          )}
        </div>
        <div className="col-span-2">
          <label className="block text-sm text-gray-600">Address</label>
          {editMode.address ? (
            <textarea
              value={tempData.address}
              onChange={(e) => handleChange("address", e.target.value)}
              className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
              rows={3}
            />
          ) : (
            <p className="text-gray-900 font-medium">{user.address}</p>
          )}
        </div>
      </div>

      {/* Insurance Policies */}
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
