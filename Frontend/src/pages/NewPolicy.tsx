import { useState } from "react";
import {
  Car,
  User,
  Shield,
  FileText,
  CreditCard,
  CheckCircle,
} from "lucide-react";
import StepIndicator from "../components/Policy/StepIndicator";
import VehicleDetails from "../components/Policy/VehicleDetails";
import PersonalInfo from "../components/Policy/PersonalInfo";
import PolicyCustomization from "../components/Policy/PolicyCustomization";
import Summary from "../components/Policy/Summary";
import Payment from "../components/Policy/Payment";
import Success from "../components/Policy/Success";

export type FormData = {
  vehicleType: string;
  registrationNumber: string;
  make: string;
  model: string;
  year: string;
  name: string;
  mobile: string;
  email: string;
  address: string;
  city: string;
  state: string;
  idv: string;
  ncb: string;
  addons: string[];
};

function Apply() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    vehicleType: "",
    registrationNumber: "",
    make: "",
    model: "",
    year: "",
    name: "",
    mobile: "",
    email: "",
    address: "",
    city: "",
    state: "",
    idv: "",
    ncb: "",
    addons: [],
  });

  const steps = [
    { number: 1, title: "Vehicle Details", icon: Car },
    { number: 2, title: "Personal Info", icon: User },
    { number: 3, title: "Customize Policy", icon: Shield },
    { number: 4, title: "Summary", icon: FileText },
    { number: 5, title: "Payment", icon: CreditCard },
    { number: 6, title: "Success", icon: CheckCircle },
  ];

  const handleNext = () => {
    setStep((prev) => Math.min(prev + 1, 6));
  };

  const handleBack = () => {
    setStep((prev) => Math.max(prev - 1, 1));
  };

  const updateFormData = (data: Partial<FormData>) => {
    setFormData((prev) => ({ ...prev, ...data }));
  };

  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <VehicleDetails
            formData={formData}
            updateFormData={updateFormData}
            onNext={handleNext}
          />
        );
      case 2:
        return (
          <PersonalInfo
            formData={formData}
            updateFormData={updateFormData}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 3:
        return (
          <PolicyCustomization
            formData={formData}
            updateFormData={updateFormData}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 4:
        return (
          <Summary
            formData={formData}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 5:
        return <Payment onNext={handleNext} onBack={handleBack} />;
      case 6:
        return <Success />;
      default:
        return null;
    }
  };

  return (
    <main className="max-w-6xl mx-auto py-8 px-4">
      <StepIndicator steps={steps} currentStep={step} />
      <div className="mt-8">{renderStep()}</div>
    </main>
  );
}

export default Apply;
