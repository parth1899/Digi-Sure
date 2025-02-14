import React from "react";
import { Shield } from "lucide-react";
import { Policy } from "../../types";
import { useNavigate } from "react-router-dom";

const policies: Policy[] = [
  {
    type: "Life",
    policyNumber: "LI-2024-001",
    sumInsured: 5000000,
    premium: 25000,
    status: "Active",
    renewalDate: "15 Dec 2024",
  },
  // Add more policies...
];

const Policies: React.FC = () => {
  const navigate = useNavigate();
  const addnewpolicy = () => {
    navigate("/NewPolicy");
  };
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">All Insurance Policies</h3>
          <button
            onClick={addnewpolicy}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
          >
            Add New Policy
          </button>
        </div>
        <div className="space-y-4">
          {policies.map((policy) => (
            <div key={policy.policyNumber} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium">{policy.type} Insurance</h4>
                  <p className="text-sm text-gray-500">
                    Policy: {policy.policyNumber}
                  </p>
                </div>
                <Shield className="w-5 h-5 text-green-600" />
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Sum Insured</p>
                  <p className="font-medium">
                    ₹{policy.sumInsured.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Premium</p>
                  <p className="font-medium">
                    ₹{policy.premium.toLocaleString()}/year
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Status</p>
                  <p className="text-green-600 font-medium">{policy.status}</p>
                </div>
                <div>
                  <p className="text-gray-600">Renewal Due</p>
                  <p className="font-medium">{policy.renewalDate}</p>
                </div>
              </div>
              <div className="mt-4 flex space-x-3">
                <button className="text-blue-600 text-sm font-medium">
                  View Details
                </button>
                <button className="text-blue-600 text-sm font-medium">
                  Download Policy
                </button>
                <button className="text-blue-600 text-sm font-medium">
                  Renew Policy
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Policies;
