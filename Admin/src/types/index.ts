export interface Policy {
  id: string;
  vehicleDetails: {
    type: string;
    make: string;
    model: string;
    registrationNumber: string;
    year: number;
  };
  personalInfo: {
    fullName: string;
    mobile: string;
    email: string;
    address: string;
    city: string;
    state: string;
    customer_id: string;
  };
  policyDetails: {
    idv: number;
    ncb: number;
    addOns: string[];
    premium: number;
    premiumBreakdown: {
      basic: number;
      addOns: number;
      gst: number;
      total: number;
    };
  };
  status: string;
  forgeryScore: number;
  documents: {
    name: string;
    type: string;
    forgeryScore: number;
  }[];
  fraudAssessment: {
    probability: number;
  };
}

interface ClaimDetails {
  claimManagementId: string;
  claimType: string;
  status: string;
  lastUpdated: string;
  fraudProbability: number;
  fraudPrediction: number;
  fraudReason: string;
  claimId: string;
  severity: string;
  vehicleAmount: number;
  totalAmount: number;
  propertyAmount: number;
  injuryAmount: number;
  claimDetailType: string;
  incident: {
    date: string;
    city: string;
    location: string;
  };
  customerId: string;
  colorCode: string;
}

export interface Claim {
  userName: string;
  claimDetails: ClaimDetails;
}
