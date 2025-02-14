import React from "react";
import { HeadphonesIcon, Mail } from "lucide-react";
import { SupportTicket } from "../../types";

// Ticket data defined once
const tickets: SupportTicket[] = [
  { id: "TKT-001", subject: "Claim Status Inquiry", status: "Open" },
  { id: "TKT-002", subject: "Policy Renewal Query", status: "Closed" },
];

const SupportTickets: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h3 className="text-lg font-semibold mb-6">Customer Support</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4">
            <HeadphonesIcon className="w-6 h-6 text-blue-600 mb-2" />
            <h4 className="font-medium mb-1">24/7 Helpline</h4>
            <p className="text-sm text-gray-600">1800-123-4567</p>
          </div>
          <div className="border rounded-lg p-4">
            <Mail className="w-6 h-6 text-blue-600 mb-2" />
            <h4 className="font-medium mb-1">Email Support</h4>
            <p className="text-sm text-gray-600">support@sbi-insurance.com</p>
          </div>
        </div>
        <div className="mt-6">
          <h4 className="font-medium mb-4">Recent Support Tickets</h4>
          <div className="space-y-3">
            {tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="flex items-center justify-between py-3 border-b last:border-0"
              >
                <div>
                  <p className="font-medium">{ticket.subject}</p>
                  <p className="text-sm text-gray-500">
                    Ticket ID: {ticket.id}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    ticket.status === "Open"
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {ticket.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportTickets; // Add the missing export
