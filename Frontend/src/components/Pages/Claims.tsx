import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import ClaimForm from "./ClaimForm";
import type { Claim, FormData } from "../../types";

const Claims: React.FC = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [showClaimForm, setShowClaimForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8081/claims/view", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch claims");
      }

      const fetchedClaims = await response.json();
      console.log(fetchedClaims);
      setClaims(fetchedClaims);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "An unknown error occurred"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitClaim = async (formData: FormData) => {
    try {
      setLoading(true);

      // Submit claim data
      const response = await fetch("http://localhost:8081/claims/detect", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Failed to submit claim");
      }

      const { claim_id } = await response.json();

      // Upload files if any
      if (formData.images.length > 0 || formData.repairBill) {
        const fileFormData = new FormData();
        formData.images.forEach((image, index) => {
          fileFormData.append(`image_${index}`, image);
        });

        if (formData.repairBill) {
          fileFormData.append("repair_bill", formData.repairBill);
        }

        const fileResponse = await fetch(`/api/claims/${claim_id}/files`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: fileFormData,
        });

        if (!fileResponse.ok) {
          throw new Error("Failed to upload files");
        }
      }

      await fetchClaims();
      setShowClaimForm(false);
      toast.success("Claim submitted successfully");
    } catch {
      toast.error("Failed to submit claim");
    } finally {
      setLoading(false);
    }
  };

  const getFraudLabel = (prediction: string) => {
    switch (prediction.toLowerCase()) {
      case "high":
        return (
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
            High Risk
          </span>
        );
      case "medium":
        return (
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
            Medium Risk
          </span>
        );
      case "low":
        return (
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
            Low Risk
          </span>
        );
      default:
        return (
          <span className="px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm">
            Pending
          </span>
        );
    }
  };

  if (loading && claims.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && claims.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchClaims}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold text-blue-900">
            Claims Management
          </h3>
          <button
            onClick={() => setShowClaimForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
            disabled={loading}
          >
            File New Claim
          </button>
        </div>
        <div className="space-y-4">
          {claims.map((claim) => (
            <div
              key={claim.id}
              className="border rounded-lg p-4 hover:border-blue-200 transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h4 className="font-medium text-blue-900">
                    {claim.type} Claim
                  </h4>
                  <p className="text-sm text-gray-500">Claim ID: {claim.id}</p>
                </div>
                <div className="flex space-x-2">
                  <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm">
                    {claim.status}
                  </span>
                  {claim.fraud_assessment &&
                    getFraudLabel(claim.fraud_assessment.prediction)}
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Filed Date</p>
                  <p className="font-medium text-blue-900">
                    {claim.incident_date}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Claim Amount</p>
                  <p className="font-medium text-blue-900">
                    ₹{claim.total_amount}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Location</p>
                  <p className="font-medium text-blue-900">
                    {claim.incident_location || "N/A"}
                  </p>
                </div>
              </div>
              {claim.fraud_assessment?.reasons && (
                <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    {claim.fraud_assessment.reasons}
                  </p>
                </div>
              )}
              <div className="mt-4 flex space-x-3">
                <button className="text-blue-600 text-sm font-medium hover:text-blue-700 transition-colors">
                  Track Status
                </button>
                <button className="text-blue-600 text-sm font-medium hover:text-blue-700 transition-colors">
                  View Documents
                </button>
                <button className="text-blue-600 text-sm font-medium hover:text-blue-700 transition-colors">
                  Contact Support
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showClaimForm && (
        <ClaimForm
          onClose={() => setShowClaimForm(false)}
          onSubmit={handleSubmitClaim}
        />
      )}
    </div>
  );
};

export default Claims;
