import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X, Upload } from "lucide-react";
import { Nominee, NomineeFormData } from "../types";

const nominees: Nominee[] = [
  { name: "Priya Kumar", relation: "Spouse", share: "60%" },
  { name: "Arjun Kumar", relation: "Son", share: "40%" },
];

const nomineeSchema = z.object({
  name: z.string().min(1, "Name is required"),
  dateOfBirth: z.string().min(1, "Date of birth is required"),
  relation: z.string().min(1, "Relationship is required"),
  aadharNumber: z.string().length(12, "Aadhar number must be 12 digits"),
  panNumber: z.string().optional(),
  mobileNumber: z.string().length(10, "Mobile number must be 10 digits"),
  email: z.string().email().optional().or(z.literal("")),
  accountNumber: z.string().optional().or(z.literal("")),
  ifscCode: z.string().optional().or(z.literal("")),
  share: z.string().min(1, "Share percentage is required"),
});

const Nominees: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<NomineeFormData>({
    resolver: zodResolver(nomineeSchema),
  });

  const onSubmit = (data: NomineeFormData) => {
    console.log(data);
    setShowForm(false);
    reset();
  };

  return (
    <div className="space-y-6 relative">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Nominee Details</h3>
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
          >
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

      {showForm && (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-30 backdrop-blur-md flex items-center justify-center p-4 z-50">
    <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Add New Nominee</h2>
          <button
            onClick={() => setShowForm(false)}
            className="text-gray-500 hover:text-gray-700 transition"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* 1. Basic Information */}
          <h3 className="text-lg font-medium text-gray-800">1. Basic Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <input
                type="text"
                {...register("name")}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
              {errors.name && <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Date of Birth</label>
              <input
                type="date"
                {...register("dateOfBirth")}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
              {errors.dateOfBirth && <p className="mt-1 text-sm text-red-600">{errors.dateOfBirth.message}</p>}
            </div>
          </div>

          {/* 2. Identity & Contact Details */}
          <h3 className="text-lg font-medium text-gray-800">2. Identity & Contact Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Aadhar Number</label>
              <input
                type="text"
                {...register("aadharNumber")}
                maxLength={12}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
              {errors.aadharNumber && <p className="mt-1 text-sm text-red-600">{errors.aadharNumber.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Mobile Number</label>
              <input
                type="tel"
                {...register("mobileNumber")}
                maxLength={10}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
              {errors.mobileNumber && <p className="mt-1 text-sm text-red-600">{errors.mobileNumber.message}</p>}
            </div>
          </div>

          {/* 3. Banking Details */}
          <h3 className="text-lg font-medium text-gray-800">3. Banking Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Account Number (Optional)</label>
              <input
                type="text"
                {...register("accountNumber")}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">IFSC Code (Optional)</label>
              <input
                type="text"
                {...register("ifscCode")}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
              />
            </div>
          </div>

          {/* 4. Share Percentage */}
          <h3 className="text-lg font-medium text-gray-800">4. Share Percentage</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700">Percentage of Benefit</label>
            <input
              type="number"
              {...register("share")}
              min="0"
              max="100"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 p-2"
            />
            {errors.share && <p className="mt-1 text-sm text-red-600">{errors.share.message}</p>}
          </div>

          {/* 5. Upload Documents (Same Formatting as Given) */}
          <h3 className="text-lg font-medium pt-4">5. Upload Documents</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Aadhar/PAN Copy</label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                      <span>Upload a file</span>
                      <input type="file" className="sr-only" accept=".pdf,.jpg,.jpeg" />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">PDF or JPEG up to 10MB</p>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Relationship Proof</label>
              <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                <div className="space-y-1 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="flex text-sm text-gray-600">
                    <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500">
                      <span>Upload a file</span>
                      <input type="file" className="sr-only" accept=".pdf,.jpg,.jpeg" />
                    </label>
                    <p className="pl-1">or drag and drop</p>
                  </div>
                  <p className="text-xs text-gray-500">PDF or JPEG up to 10MB</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-4 mt-4">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition"
            >
              Add Nominee
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
)}
    </div>
  );
};

export default Nominees;