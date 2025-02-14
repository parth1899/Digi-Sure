import React from "react";
import { DivideIcon as LucideIcon } from "lucide-react";

type Step = {
  number: number;
  title: string;
  icon: typeof LucideIcon;
};

type Props = {
  steps: Step[];
  currentStep: number;
};

const StepIndicator: React.FC<Props> = ({ steps, currentStep }) => {
  return (
    <div className="hidden md:flex justify-between items-center">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isActive = step.number === currentStep;
        const isCompleted = step.number < currentStep;

        return (
          <React.Fragment key={step.number}>
            {index > 0 && (
              <div
                className={`flex-1 h-1 ${
                  isCompleted ? "bg-blue-600" : "bg-gray-300"
                }`}
              />
            )}
            <div className="flex flex-col items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : isCompleted
                    ? "bg-green-500 text-white"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                <Icon size={20} />
              </div>
              <span
                className={`mt-2 text-sm font-medium ${
                  isActive ? "text-blue-600" : "text-gray-500"
                }`}
              >
                {step.title}
              </span>
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default StepIndicator;
