import React from "react";
import { CreditCard } from "lucide-react";
import { PaymentMethod, Transaction } from "../../types";

const paymentMethods: PaymentMethod[] = [
  {
    type: "HDFC Bank Credit Card",
    lastFour: "4589",
    isPrimary: true,
  },
];

const transactions: Transaction[] = [
  {
    id: "TXN001",
    policy: "Health Insurance",
    amount: 15000,
    date: "01 Mar 2024",
    status: "Paid",
  },
];

const Payments: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-6">Payment Methods</h3>
        <div className="space-y-4">
          {paymentMethods.map((method, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <CreditCard className="w-6 h-6 text-gray-600" />
                  <div>
                    <p className="font-medium">{method.type}</p>
                    <p className="text-sm text-gray-500">
                      Ending in {method.lastFour}
                    </p>
                  </div>
                </div>
                {method.isPrimary && (
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    Primary
                  </span>
                )}
              </div>
            </div>
          ))}
          <button className="w-full border border-dashed rounded-lg p-4 text-gray-600 hover:text-blue-600 hover:border-blue-600">
            + Add New Payment Method
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-6">Recent Transactions</h3>
        <div className="space-y-4">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between py-3 border-b last:border-0"
            >
              <div>
                <p className="font-medium">{transaction.policy} Premium</p>
                <p className="text-sm text-gray-500">{transaction.date}</p>
              </div>
              <div className="text-right">
                <p className="font-medium">
                  ₹{transaction.amount.toLocaleString()}
                </p>
                <p className="text-sm text-green-600">{transaction.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Payments;
