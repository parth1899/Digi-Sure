import React, { useEffect } from "react";
import { CheckCircle, Download, MessageCircle, Check, FileText } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Success: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md p-8 text-center">
      <div className="mb-6">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
      </div>

      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Payment Successful!
      </h2>

      <p className="text-gray-600 mb-8">
        Your SBI General Car Insurance policy has been issued successfully.
        Policy documents have been sent to your email.
      </p>

      <div className="space-y-4">
        <button className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
          <Download size={20} />
          <span>Download Policy Document</span>
        </button>

        <button className="w-full flex items-center justify-center space-x-2 border border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2">
          <MessageCircle size={20} />
          <span>Contact Support</span>
        </button>
      </div>

      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-semibold text-gray-800 mb-2">Policy Details</h3>
        <div className="text-sm text-gray-600">
          <p>Policy Number: SBIG-2025-CAR-123456</p>
          <p>Valid Till: March 14, 2026</p>
        </div>
      </div>

      <div className="mt-8">
        <p className="text-gray-600 mb-4">
          To complete the process and for admin verification, please upload your required documents.
        </p>
        <button
          onClick={() => navigate("/dashboard/documents")}
          className="w-full flex items-center justify-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        >
          <FileText size={20} />
          <span>Upload Documents</span>
        </button>
      </div>
    </div>
  );
};

export default Success;
