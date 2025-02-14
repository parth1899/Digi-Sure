import React from "react";
import { Nominee } from "../../types";

const nominees: Nominee[] = [
  { name: "Priya Kumar", relation: "Spouse", share: "60%" },
  { name: "Arjun Kumar", relation: "Son", share: "40%" },
];

const Nominees: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Nominee Details</h3>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            Add Nominee
          </button>
        </div>
        <div className="space-y-4">
          {nominees.map((nominee, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">{nominee.name}</h4>
                  <p className="text-sm text-gray-500">{nominee.relation}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{nominee.share}</p>
                  <p className="text-sm text-gray-500">Share</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Nominees;
