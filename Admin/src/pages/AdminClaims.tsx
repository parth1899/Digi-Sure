import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, Check, X } from 'lucide-react';

interface Claim {
  id: string;
  userName: string;
  claimType: string;
  amount: number;
  submissionDate: string;
  isFraudulent: boolean;
  fraudReason?: string;
  status: 'Pending' | 'Approved' | 'Rejected';
  details: string;
}

const mockClaims: Claim[] = [
  {
    id: 'CLM-001',
    userName: 'John Doe',
    claimType: 'Medical',
    amount: 5000,
    submissionDate: '2024-03-10',
    isFraudulent: true,
    fraudReason: 'Duplicate claim detected',
    status: 'Pending',
    details: 'Emergency room visit for acute appendicitis',
  },
  {
    id: 'CLM-002',
    userName: 'Jane Smith',
    claimType: 'Accident',
    amount: 3000,
    submissionDate: '2024-03-09',
    isFraudulent: false,
    status: 'Pending',
    details: 'Vehicle damage repair after minor collision',
  },
];

const AdminClaims = () => {
  const [expandedClaim, setExpandedClaim] = useState<string | null>(null);

  const toggleExpand = (claimId: string) => {
    setExpandedClaim(expandedClaim === claimId ? null : claimId);
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Claims Management</h1>
      
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"></th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Claim ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fraud Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {mockClaims.map((claim) => (
              <React.Fragment key={claim.id}>
                <tr className={`${claim.isFraudulent ? 'bg-red-50' : ''} hover:bg-gray-50`}>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => toggleExpand(claim.id)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedClaim === claim.id ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{claim.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{claim.userName}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{claim.claimType}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${claim.amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                      ${claim.status === 'Approved' ? 'bg-green-100 text-green-800' : 
                        claim.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' : 
                        'bg-red-100 text-red-800'}`}>
                      {claim.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {claim.isFraudulent ? (
                      <div className="flex items-center text-red-600">
                        <AlertTriangle size={16} className="mr-2" />
                        <span>Fraudulent</span>
                      </div>
                    ) : (
                      <span className="text-green-600">Valid</span>
                    )}
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
                {expandedClaim === claim.id && (
                  <tr className={claim.isFraudulent ? 'bg-red-50' : 'bg-gray-50'}>
                    <td colSpan={8} className="px-6 py-4">
                      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <h4 className="text-gray-900 font-semibold mb-4">Claim Details</h4>
                        <p className="text-gray-700 mb-4">{claim.details}</p>
                        {claim.isFraudulent && claim.fraudReason && (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
                            <h5 className="text-red-600 font-semibold flex items-center">
                              <AlertTriangle size={16} className="mr-2" />
                              Fraud Detection Details
                            </h5>
                            <p className="text-red-700 mt-2">{claim.fraudReason}</p>
                          </div>
                        )}
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

export default AdminClaims;