import React, { useState } from 'react';
import { Check, X, ChevronDown, ChevronUp, AlertTriangle, Car, Truck as Truck2 } from 'lucide-react';

interface Policy {
  id: string;
  vehicleDetails: {
    type: 'Car' | 'SUV' | 'Two Wheeler';
    registrationNumber: string;
    make: string;
    model: string;
    year: number;
  };
  personalInfo: {
    fullName: string;
    mobile: string;
    email: string;
    address: string;
    city: string;
    state: string;
  };
  policyDetails: {
    idv: number;
    ncb: number;
    addOns: string[];
    premiumBreakdown: {
      basic: number;
      addOns: number;
      gst: number;
      total: number;
    };
  };
  status: 'Pending' | 'Active' | 'Rejected';
  forgeryScore: number;
  documents: {
    name: string;
    type: string;
    forgeryScore: number;
  }[];
}

const mockPolicies: Policy[] = [
  {
    id: 'POL-001',
    vehicleDetails: {
      type: 'Car',
      registrationNumber: 'KA01AB1234',
      make: 'Honda',
      model: 'City',
      year: 2022
    },
    personalInfo: {
      fullName: 'John Doe',
      mobile: '9988776655',
      email: 'john@example.com',
      address: '123 Main St',
      city: 'Bangalore',
      state: 'Karnataka'
    },
    policyDetails: {
      idv: 40000,
      ncb: 0,
      addOns: ['Zero Depreciation', 'Engine Protection'],
      premiumBreakdown: {
        basic: 15000,
        addOns: 3500,
        gst: 3330,
        total: 21830
      }
    },
    status: 'Pending',
    forgeryScore: 75,
    documents: [
      { name: 'Aadhar Card', type: 'ID', forgeryScore: 82 },
      { name: 'PAN Card', type: 'Tax', forgeryScore: 68 },
    ],
  },
  {
    id: 'POL-002',
    vehicleDetails: {
      type: 'SUV',
      registrationNumber: 'MH02CD5678',
      make: 'Toyota',
      model: 'Fortuner',
      year: 2023
    },
    personalInfo: {
      fullName: 'Jane Smith',
      mobile: '9876543210',
      email: 'jane@example.com',
      address: '456 Park Avenue',
      city: 'Mumbai',
      state: 'Maharashtra'
    },
    policyDetails: {
      idv: 60000,
      ncb: 20,
      addOns: ['Roadside Assistance', 'Personal Accident Cover'],
      premiumBreakdown: {
        basic: 20000,
        addOns: 4500,
        gst: 4410,
        total: 28910
      }
    },
    status: 'Active',
    forgeryScore: 15,
    documents: [
      { name: 'Aadhar Card', type: 'ID', forgeryScore: 12 },
      { name: 'Medical Report', type: 'Health', forgeryScore: 18 },
    ],
  },
];

const AdminPolicies = () => {
  const [expandedPolicy, setExpandedPolicy] = useState<string | null>(null);

  const toggleExpand = (policyId: string) => {
    setExpandedPolicy(expandedPolicy === policyId ? null : policyId);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Policy Management</h1>
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Policy ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vehicle</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Premium</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Forgery Score</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mockPolicies.map((policy) => (
              <React.Fragment key={policy.id}>
                <tr className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <button
                      onClick={() => toggleExpand(policy.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedPolicy === policy.id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{policy.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      {policy.vehicleDetails.type === 'Car' ? <Car size={16} className="mr-2" /> : <Truck2 size={16} className="mr-2" />}
                      {policy.vehicleDetails.make} {policy.vehicleDetails.model}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{policy.personalInfo.fullName}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatCurrency(policy.policyDetails.premiumBreakdown.total)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                      ${policy.status === 'Active' ? 'bg-green-100 text-green-800' : 
                        policy.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-red-100 text-red-800'}`}>
                      {policy.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`text-sm ${
                        policy.forgeryScore > 50 ? 'text-red-600' : 'text-green-600'
                      }`}>
                        {policy.forgeryScore}%
                      </span>
                      {policy.forgeryScore > 50 && (
                        <AlertTriangle size={16} className="ml-2 text-red-500" />
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-green-600 hover:text-green-700">
                        <Check size={20} />
                      </button>
                      <button className="text-red-600 hover:text-red-700">
                        <X size={20} />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedPolicy === policy.id && (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 bg-gray-50">
                      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                          {/* Vehicle Details */}
                          <div className="space-y-4">
                            <h4 className="text-lg font-semibold text-gray-900">Vehicle Details</h4>
                            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Vehicle Type:</span>
                                <span className="text-gray-900">{policy.vehicleDetails.type}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Registration Number:</span>
                                <span className="text-gray-900">{policy.vehicleDetails.registrationNumber}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Make & Model:</span>
                                <span className="text-gray-900">{policy.vehicleDetails.make} {policy.vehicleDetails.model}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Year:</span>
                                <span className="text-gray-900">{policy.vehicleDetails.year}</span>
                              </div>
                            </div>
                          </div>

                          {/* Personal Information */}
                          <div className="space-y-4">
                            <h4 className="text-lg font-semibold text-gray-900">Personal Information</h4>
                            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Name:</span>
                                <span className="text-gray-900">{policy.personalInfo.fullName}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Mobile:</span>
                                <span className="text-gray-900">{policy.personalInfo.mobile}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Email:</span>
                                <span className="text-gray-900">{policy.personalInfo.email}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Address:</span>
                                <span className="text-gray-900">{policy.personalInfo.address}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">City:</span>
                                <span className="text-gray-900">{policy.personalInfo.city}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">State:</span>
                                <span className="text-gray-900">{policy.personalInfo.state}</span>
                              </div>
                            </div>
                          </div>

                          {/* Policy Details */}
                          <div className="space-y-4">
                            <h4 className="text-lg font-semibold text-gray-900">Policy Details</h4>
                            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                              <div className="flex justify-between">
                                <span className="text-gray-600">IDV:</span>
                                <span className="text-gray-900">{formatCurrency(policy.policyDetails.idv)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">NCB:</span>
                                <span className="text-gray-900">{policy.policyDetails.ncb}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Selected Add-ons:</span>
                                <span className="text-gray-900">{policy.policyDetails.addOns.join(', ')}</span>
                              </div>
                              <div className="mt-4 pt-4 border-t border-gray-200">
                                <h5 className="font-semibold text-gray-900 mb-2">Premium Breakdown</h5>
                                <div className="space-y-2">
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Basic Premium</span>
                                    <span className="text-gray-900">{formatCurrency(policy.policyDetails.premiumBreakdown.basic)}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">Add-ons</span>
                                    <span className="text-gray-900">{formatCurrency(policy.policyDetails.premiumBreakdown.addOns)}</span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-600">GST (18%)</span>
                                    <span className="text-gray-900">{formatCurrency(policy.policyDetails.premiumBreakdown.gst)}</span>
                                  </div>
                                  <div className="flex justify-between pt-2 border-t border-gray-300 font-semibold">
                                    <span className="text-gray-900">Total Premium</span>
                                    <span className="text-gray-900">{formatCurrency(policy.policyDetails.premiumBreakdown.total)}</span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Document Verification */}
                          <div className="lg:col-span-3 space-y-4">
                            <h4 className="text-lg font-semibold text-gray-900">Document Verification</h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {policy.documents.map((doc, index) => (
                                <div key={index} className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                                  <div className="flex justify-between items-center">
                                    <div>
                                      <p className="text-gray-900 font-medium">{doc.name}</p>
                                      <p className="text-gray-500 text-sm">{doc.type}</p>
                                    </div>
                                    <div className={`text-sm ${
                                      doc.forgeryScore > 50 ? 'text-red-600' : 'text-green-600'
                                    }`}>
                                      {doc.forgeryScore}% forgery score
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminPolicies;