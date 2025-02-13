import React from "react";
import { FormData } from "../pages/apply";

type Props = {
  formData: FormData;
  onNext: () => void;
  onBack: () => void;
};

const Summary: React.FC<Props> = ({ formData, onNext, onBack }) => {
  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Policy Summary</h2>

      <div className="space-y-6">
        <section>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Vehicle Details
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Vehicle Type:</span>
              <p className="font-medium">{formData.vehicleType}</p>
            </div>
            <div>
              <span className="text-gray-500">Registration Number:</span>
              <p className="font-medium">{formData.registrationNumber}</p>
            </div>
            <div>
              <span className="text-gray-500">Make & Model:</span>
              <p className="font-medium">
                {formData.make} {formData.model}
              </p>
            </div>
            <div>
              <span className="text-gray-500">Year:</span>
              <p className="font-medium">{formData.year}</p>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Personal Information
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Name:</span>
              <p className="font-medium">{formData.name}</p>
            </div>
            <div>
              <span className="text-gray-500">Mobile:</span>
              <p className="font-medium">{formData.mobile}</p>
            </div>
            <div>
              <span className="text-gray-500">Email:</span>
              <p className="font-medium">{formData.email}</p>
            </div>
            <div>
              <span className="text-gray-500">Address:</span>
              <p className="font-medium">{formData.address}</p>
            </div>
            <div>
              <span className="text-gray-500">City:</span>
              <p className="font-medium">{formData.city}</p>
            </div>
            <div>
              <span className="text-gray-500">State:</span>
              <p className="font-medium">{formData.state}</p>
            </div>
          </div>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-gray-700 mb-3">
            Policy Details
          </h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">IDV:</span>
              <p className="font-medium">₹{formData.idv}</p>
            </div>
            <div>
              <span className="text-gray-500">NCB:</span>
              <p className="font-medium">{formData.ncb}%</p>
            </div>
          </div>
          <div className="mt-4">
            <span className="text-gray-500">Selected Add-ons:</span>
            <ul className="list-disc list-inside mt-2">
              {formData.addons?.map((addon) => (
                <li key={addon} className="font-medium">
                  {addon}
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">
            Premium Breakdown
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Basic Premium</span>
              <span>₹15,000</span>
            </div>
            <div className="flex justify-between">
              <span>Add-ons</span>
              <span>₹3,500</span>
            </div>
            <div className="flex justify-between">
              <span>GST (18%)</span>
              <span>₹3,330</span>
            </div>
            <div className="border-t border-gray-300 pt-2 mt-2">
              <div className="flex justify-between font-semibold">
                <span>Total Premium</span>
                <span>₹21,830</span>
              </div>
            </div>
          </div>
        </section>

        <div className="flex items-center mt-6">
          <input
            type="checkbox"
            id="terms"
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            required
          />
          <label htmlFor="terms" className="ml-2 text-sm text-gray-600">
            I accept the Terms & Conditions and confirm that all the information
            provided is accurate
          </label>
        </div>

        <div className="flex justify-between">
          <button
            onClick={onBack}
            className="text-gray-600 px-6 py-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Back
          </button>
          <button
            onClick={onNext}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Proceed to Payment
          </button>
        </div>
      </div>
    </div>
  );
};

export default Summary;
