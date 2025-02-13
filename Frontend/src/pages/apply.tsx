import { useState } from "react";
import {
  Car,
  User,
  Shield,
  FileText,
  CreditCard,
  CheckCircle,
} from "lucide-react";
import StepIndicator from "../components/StepIndicator";
import VehicleDetails from "../components/VehicleDetails";
import PersonalInfo from "../components/PersonalInfo";
import PolicyCustomization from "../components/PolicyCustomization";
import Summary from "../components/Summary";
import Payment from "../components/Payment";
import Success from "../components/Success";

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
    // <div className="min-h-screen bg-gray-50">
    //   {/* <header className="bg-blue-700 text-white py-4 px-6 shadow-lg">
    //     <div className="max-w-6xl mx-auto flex items-center justify-between">
    //       <div className="flex items-center space-x-2">
    //         <Shield size={32} />
    //         <h1 className="text-2xl font-bold">SBI General Car Insurance</h1>
    //       </div>
    //       <nav className="hidden md:flex space-x-6">
    //         <a href="#" className="hover:text-blue-200">
    //           Help
    //         </a>
    //         <a href="#" className="hover:text-blue-200">
    //           Support
    //         </a>
    //         <a
    //           href="#"
    //           className="bg-white text-blue-700 px-4 py-2 rounded-lg font-medium hover:bg-blue-50"
    //         >
    //           Login
    //         </a>
    //       </nav>
    //     </div>
    //   </header> */}

    // </div>
    <main className="max-w-6xl mx-auto py-8 px-4">
      <StepIndicator steps={steps} currentStep={step} />
      <div className="mt-8">{renderStep()}</div>
    </main>
  );
}

export default Apply;
