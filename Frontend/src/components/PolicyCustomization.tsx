import React from "react";
import { FormData } from "../pages/apply";

type Props = {
  formData: FormData;
  updateFormData: (data: Partial<FormData>) => void;
  onNext: () => void;
  onBack: () => void;
};

const PolicyCustomization: React.FC<Props> = ({
  formData,
  updateFormData,
  onNext,
  onBack,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onNext();
  };

  const handleAddonChange = (addon: string) => {
    const currentAddons = formData.addons || [];
    const newAddons = currentAddons.includes(addon)
      ? currentAddons.filter((a) => a !== addon)
      : [...currentAddons, addon];
    updateFormData({ addons: newAddons });
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md p-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">
        Customize Your Policy
      </h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Insured Declared Value (IDV)
          </label>
          <input
            type="number"
            value={formData.idv}
            onChange={(e) => updateFormData({ idv: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter IDV amount"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            No Claim Bonus (NCB)
          </label>
          <select
            value={formData.ncb}
            onChange={(e) => updateFormData({ ncb: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            required
          >
            <option value="">Select NCB</option>
            <option value="0">0%</option>
            <option value="20">20%</option>
            <option value="25">25%</option>
            <option value="35">35%</option>
            <option value="45">45%</option>
            <option value="50">50%</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-4">
            Add-on Covers
          </label>
          <div className="space-y-3">
            {[
              "Zero Depreciation",
              "Engine Protection",
              "Roadside Assistance",
              "Consumables Cover",
              "Personal Accident Cover",
            ].map((addon) => (
              <label key={addon} className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.addons?.includes(addon)}
                  onChange={() => handleAddonChange(addon)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-gray-700">{addon}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-8 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Premium Estimate
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
        </div>

        <div className="flex justify-between">
          <button
            type="button"
            onClick={onBack}
            className="text-gray-600 px-6 py-2 rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          >
            Back
          </button>
          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Next
          </button>
        </div>
      </form>
    </div>
  );
};

export default PolicyCustomization;
