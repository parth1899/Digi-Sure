const Security: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-6">Security Settings</h3>
        <div className="space-y-6">
          <div className="flex items-center justify-between pb-4 border-b">
            <div>
              <h4 className="font-medium">Two-Factor Authentication</h4>
              <p className="text-sm text-gray-600">
                Add an extra layer of security to your account
              </p>
            </div>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
              Enable
            </button>
          </div>
          <div className="flex items-center justify-between pb-4 border-b">
            <div>
              <h4 className="font-medium">Change Password</h4>
              <p className="text-sm text-gray-600">
                Update your password regularly for better security
              </p>
            </div>
            <button className="text-blue-600 text-sm font-medium">
              Update
            </button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium">Login History</h4>
              <p className="text-sm text-gray-600">
                Monitor your account access
              </p>
            </div>
            <button className="text-blue-600 text-sm font-medium">
              View All
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Security;
