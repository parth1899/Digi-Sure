import React from "react";
import { FileText, User, ClipboardList } from "lucide-react";
import { Document } from "../../types";

const documents: Document[] = [
  {
    name: "Policy Documents",
    icon: FileText,
    count: 3,
    type: "",
  },
  {
    name: "KYC Documents",
    icon: User,
    count: 2,
    type: "",
  },
  {
    name: "Medical Reports",
    icon: FileText,
    count: 1,
    type: "",
  },
  {
    name: "Claim Documents",
    icon: ClipboardList,
    count: 1,
    type: "",
  },
];

const Documents: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Documents Vault</h3>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            Upload Document
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map((doc, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center space-x-3">
                {React.createElement(doc.icon)}
                <div>
                  <p className="font-medium">{doc.name}</p>
                  <p className="text-sm text-gray-500">{doc.count} documents</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Documents;
