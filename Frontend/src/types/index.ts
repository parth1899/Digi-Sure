export interface User {
  name: string;
  customerId: string;
  email: string;
  phone: string;
  address: string;
  activePolicies: number;
}

export interface Policy {
  type: string;
  policyNumber: string;
  sumInsured: number;
  premium: number;
  status: string;
  renewalDate: string;
  vehicle?: {
    make: string;
    model: string;
    year: string;
    registration: string;
  };
}

export interface Claim {
  id: string;
  type: string;
  status: string;
  amount: number;
  date: string;
  details: string;
}

export interface PaymentMethod {
  type: string;
  lastFour: string;
  isPrimary: boolean;
}

export interface Transaction {
  id: string;
  policy: string;
  amount: number;
  date: string;
  status: string;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  count: number;
  uploadedOn: Date;
  size: number;
  icon: React.ComponentType; // This would be a Lucide icon component type
}

export interface Nominee {
  name: string;
  relation: string;
  share: string;
}

export interface SupportTicket {
  id: string;
  subject: string;
  status: string;
}

export interface NomineeFormData {
  name: string;
  dateOfBirth: string;
  relation: string;
  aadharNumber: string;
  panNumber?: string;
  mobileNumber: string;
  email?: string;
  accountNumber?: string;
  ifscCode?: string;
  share: string;
}
