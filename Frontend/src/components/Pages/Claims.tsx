import React from "react";
import { Claim } from "../../types";

const claims: Claim[] = [
  {
    id: "CLM-2024-001",
    type: "Health Insurance",
    status: "In Progress",
    amount: 75000,
    date: "01 Mar 2024",
    details: "Hospitalization",
  },
];

const Claims: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Claims Management</h3>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            File New Claim
          </button>
        </div>
        <div className="space-y-4">
          {claims.map((claim) => (
            <div key={claim.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium">{claim.type} Claim</h4>
                  <p className="text-sm text-gray-500">Claim ID: {claim.id}</p>
                </div>
                <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                  {claim.status}
                </span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Filed Date</p>
                  <p className="font-medium">{claim.date}</p>
                </div>
                <div>
                  <p className="text-gray-600">Claim Amount</p>
                  <p className="font-medium">
                    ₹{claim.amount.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Type</p>
                  <p className="font-medium">{claim.details}</p>
                </div>
              </div>
              <div className="mt-4 flex space-x-3">
                <button className="text-blue-600 text-sm font-medium">
                  Track Status
                </button>
                <button className="text-blue-600 text-sm font-medium">
                  View Documents
                </button>
                <button className="text-blue-600 text-sm font-medium">
                  Contact Support
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Claims;
