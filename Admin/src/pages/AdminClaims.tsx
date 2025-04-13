import React, { useState, useEffect } from "react";
import { AlertTriangle, ChevronDown, ChevronUp, Check, X } from "lucide-react";
import { Claim } from "../types";

const AdminClaims = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [expandedClaim, setExpandedClaim] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      const response = await fetch("http://localhost:8081/admin/claims");
      if (!response.ok) {
        throw new Error("Failed to fetch claims");
      }
      const data = (await response.json()) as Claim[];
      console.log(data);

      // Deduplicate claims based on claimManagementId
      const dedupedClaims = Array.from(
        new Map(
          data.map((claim: Claim) => [
            claim.claimDetails.claimManagementId,
            claim,
          ])
        ).values()
      );

      setClaims(dedupedClaims);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (claimId: string) => {
    setExpandedClaim(expandedClaim === claimId ? null : claimId);
  };

  const updateClaimStatus = async (
    claimManagementId: string,
    newStatus: string
  ) => {
    try {
      const response = await fetch(
        `http://localhost:8081/admin/claims/${claimManagementId}/status`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: newStatus }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to update claim status");
      }

      // Update local state after successful backend update
      setClaims((prevClaims) =>
        prevClaims.map((claim) =>
          claim.claimDetails.claimManagementId === claimManagementId
            ? {
                ...claim,
                claimDetails: {
                  ...claim.claimDetails,
                  status: newStatus,
                },
              }
            : claim
        )
      );
    } catch (error) {
      console.error("Error updating claim status: ", error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-red-600">
        Error loading claims: {error}
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Claims Management
      </h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="w-10 px-3 py-3"></th>
              <th className="w-1/6 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Claim ID
              </th>
              <th className="w-1/6 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="w-1/6 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th className="w-1/6 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Amount
              </th>
              <th className="w-1/8 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="w-1/8 px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fraud Score
              </th>
              <th className="w-20 px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {claims.map((claim) => (
              <React.Fragment key={claim.claimDetails.claimManagementId}>
                <tr
                  className={`${
                    claim.claimDetails.colorCode === "#FF0000"
                      ? "bg-red-50"
                      : ""
                  } hover:bg-gray-50`}
                >
                  <td className="px-6 py-4">
                    <button
                      onClick={() =>
                        toggleExpand(claim.claimDetails.claimManagementId)
                      }
                      className="text-gray-400 hover:text-gray-600"
                    >
                      {expandedClaim ===
                      claim.claimDetails.claimManagementId ? (
                        <ChevronUp size={20} />
                      ) : (
                        <ChevronDown size={20} />
                      )}
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {claim.claimDetails.claimManagementId}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {claim.userName}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {claim.claimDetails.claimType}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${claim.claimDetails.totalAmount?.toLocaleString() ?? 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        claim.claimDetails.status === "Approved"
                          ? "bg-green-100 text-green-800"
                          : claim.claimDetails.status === "In Progress"
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-red-100 text-red-800"
                      }`}
                    >
                      {claim.claimDetails.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {claim.claimDetails.colorCode === "#FF0000" ? (
                      <div className="flex items-center text-red-600">
                        <AlertTriangle size={16} className="mr-2" />
                        <span>Fraudulent</span>
                      </div>
                    ) : (
                      <span className="text-green-600">Valid</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center justify-center space-x-4">
                      <button
                        onClick={() =>
                          updateClaimStatus(
                            claim.claimDetails.claimManagementId,
                            "Approved"
                          )
                        }
                        className="text-green-600 hover:text-green-700 p-1"
                      >
                        <Check size={20} />
                      </button>
                      <button
                        onClick={() =>
                          updateClaimStatus(
                            claim.claimDetails.claimManagementId,
                            "Rejected"
                          )
                        }
                        className="text-red-600 hover:text-red-700 p-1"
                      >
                        <X size={20} />
                      </button>
                    </div>
                  </td>
                </tr>
                {expandedClaim === claim.claimDetails.claimManagementId && (
                  <tr
                    className={
                      claim.claimDetails.colorCode === "#FF0000"
                        ? "bg-red-50"
                        : "bg-gray-50"
                    }
                  >
                    <td colSpan={8} className="px-6 py-4">
                      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                        <h4 className="text-gray-900 font-semibold mb-4">
                          Claim Details
                        </h4>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm text-gray-600">
                              Severity: {claim.claimDetails.severity}
                            </p>
                            <p className="text-sm text-gray-600">
                              Vehicle Amount:{" "}
                              {claim.claimDetails.vehicleAmount?.toLocaleString() ??
                                0}
                            </p>
                            <p className="text-sm text-gray-600">
                              Property Amount:{" "}
                              {claim.claimDetails.propertyAmount?.toLocaleString() ??
                                0}
                            </p>
                            <p className="text-sm text-gray-600">
                              Injury Amount:{" "}
                              {claim.claimDetails.injuryAmount?.toLocaleString() ??
                                0}
                            </p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-600">
                              Incident Date: {claim.claimDetails.incident.date}
                            </p>
                            <p className="text-sm text-gray-600">
                              Incident Location:{" "}
                              {claim.claimDetails.incident.location}
                            </p>
                            <p className="text-sm text-gray-600">
                              Incident City: {claim.claimDetails.incident.city}
                            </p>
                            <p className="text-sm text-gray-600">
                              Customer ID: {claim.claimDetails.customerId}
                            </p>
                          </div>
                        </div>
                        {claim.claimDetails.colorCode === "#FF0000" &&
                          claim.claimDetails.fraudReason && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
                              <h5 className="text-red-600 font-semibold flex items-center">
                                <AlertTriangle size={16} className="mr-2" />
                                Fraud Detection Details
                              </h5>
                              <p className="text-red-700 mt-2">
                                Fraud Probability:{" "}
                                {(
                                  claim.claimDetails.fraudProbability * 100
                                ).toFixed(1)}
                                %
                              </p>
                              <p className="text-red-700">
                                Reason: {claim.claimDetails.fraudReason}
                              </p>
                            </div>
                          )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminClaims;
