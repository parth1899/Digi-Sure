import React, { useMemo } from "react";
import { FormData } from "../../pages/NewPolicy";

type Props = {
  formData: FormData;
  updateFormData: (data: Partial<FormData>) => void;
  onNext: () => void;
  onBack: () => void;
};
const generatePolicyNumber = () => {
  return Math.floor(100000 + Math.random() * 900000).toString();
};
// Premium calculation utilities
const calculatePremiums = (formData: FormData) => {
  const { idv, ncb, addons = [] } = formData;

  // Base calculations
  const baseRate = 0.03; // 3% of IDV as base premium
  let basicPremium = Number(idv) * baseRate;

  // Apply NCB discount
  const ncbDiscount = (Number(ncb) / 100) * basicPremium;
  basicPremium -= ncbDiscount;

  // Calculate add-on costs
  const addonRates: Record<string, number> = {
    "Zero Depreciation": 0.15,
    "Engine Protection": 0.1,
    "Roadside Assistance": 0.05,
    "Consumables Cover": 0.08,
    "Personal Accident Cover": 0.12,
  };

  const addonsTotal = addons.reduce((sum, addon) => {
    return sum + basicPremium * (addonRates[addon] || 0);
  }, 0);

  // Calculate GST
  const subtotal = basicPremium + addonsTotal;
  const gst = subtotal * 0.18;
  const total = subtotal + gst;

  // Calculate other policy values
  const policy_annual_premium = total;
  const umbrella_limit = Math.max(Number(idv) * 1.5, 1000000); // 1.5x IDV or minimum 10L
  const policy_csl = Math.min(umbrella_limit * 0.8, 5000000); // 80% of umbrella limit, max 50L
  const total_insurance_amount = Number(idv) + policy_csl;

  return {
    basicPremium: Math.round(basicPremium),
    addonsTotal: Math.round(addonsTotal),
    gst: Math.round(gst),
    total: Math.round(total),
    policy_annual_premium: Math.round(policy_annual_premium),
    umbrella_limit: Math.round(umbrella_limit),
    policy_csl: Math.round(policy_csl),
    total_insurance_amount: Math.round(total_insurance_amount),
  };
};

const PolicyCustomization: React.FC<Props> = ({
  formData,
  updateFormData,
  onNext,
  onBack,
}) => {
  React.useEffect(() => {
    if (!formData.policy_number) {
      updateFormData({ policy_number: generatePolicyNumber() });
    }
  }, []);
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

  // Calculate premiums whenever form data changes
  const premiums = useMemo(() => calculatePremiums(formData), [formData]);

  // Update formData with calculated values
  React.useEffect(() => {
    updateFormData({
      policy_annual_premium: premiums.policy_annual_premium,
      umbrella_limit: premiums.umbrella_limit,
      policy_csl: premiums.policy_csl,
      total_insurance_amount: premiums.total_insurance_amount,
    });
  }, [premiums, updateFormData]);

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
            Premium Details
          </h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Basic Premium</span>
              <span>₹{premiums.basicPremium.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Add-ons</span>
              <span>₹{premiums.addonsTotal.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>GST (18%)</span>
              <span>₹{premiums.gst.toLocaleString()}</span>
            </div>
            <div className="border-t border-gray-300 pt-2 mt-2">
              <div className="flex justify-between font-semibold">
                <span>Total Premium</span>
                <span>₹{premiums.total.toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 space-y-2 pt-4 border-t border-gray-300">
            <h4 className="font-semibold text-gray-800">
              Policy Coverage Details
            </h4>
            <div className="flex justify-between">
              <span>Annual Premium</span>
              <span>₹{premiums.policy_annual_premium.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Umbrella Limit</span>
              <span>₹{premiums.umbrella_limit.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span>Combined Single Limit</span>
              <span>₹{premiums.policy_csl.toLocaleString()}</span>
            </div>
            <div className="flex justify-between font-semibold">
              <span>Total Insurance Amount</span>
              <span>₹{premiums.total_insurance_amount.toLocaleString()}</span>
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
