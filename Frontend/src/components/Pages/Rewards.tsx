import { Gift, Users } from "lucide-react";

const Reward: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-6">Rewards & Referrals</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="border rounded-lg p-4">
            <Gift className="w-6 h-6 text-blue-600 mb-2" />
            <h4 className="font-medium">Reward Points</h4>
            <p className="text-2xl font-bold text-blue-600 mb-2">2,500</p>
            <p className="text-sm text-gray-600">
              Worth ₹2,500 in premium discounts
            </p>
          </div>
          <div className="border rounded-lg p-4">
            <Users className="w-6 h-6 text-blue-600 mb-2" />
            <h4 className="font-medium">Successful Referrals</h4>
            <p className="text-2xl font-bold text-blue-600 mb-2">3</p>
            <p className="text-sm text-gray-600">Earned ₹1,500 in cashback</p>
          </div>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Refer & Earn</h4>
          <p className="text-sm text-gray-600 mb-4">
            Get ₹500 for each successful referral
          </p>
          <div className="flex space-x-3">
            <input
              type="text"
              value="RAJESH500"
              readOnly
              className="flex-1 px-3 py-2 border rounded-lg bg-white"
            />
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
              Copy Code
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Reward;
