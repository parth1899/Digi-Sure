import React from "react";
import { User } from "../../types";

interface InputFieldProps {
  label: string;
  field: keyof User;
  value: string;
  onChange: (field: keyof User, value: string) => void;
}

export const InputField: React.FC<InputFieldProps> = ({
  label,
  field,
  value,
  onChange,
}) => {
  // Special handling for different field types
  if (field === "dob") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <input
          type="date"
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
    );
  }

  if (field === "sex") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <select
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Other">Other</option>
          <option value="Prefer not to say">Prefer not to say</option>
        </select>
      </div>
    );
  }

  if (field === "education_level") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <select
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select</option>
          <option value="High School">High School</option>
          <option value="Diploma">Diploma</option>
          <option value="Bachelor's Degree">Bachelor's Degree</option>
          <option value="Master's Degree">Master's Degree</option>
          <option value="Doctorate">Doctorate</option>
          <option value="Other">Other</option>
        </select>
      </div>
    );
  }

  if (field === "occupation") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <select
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select</option>
          <option value="Student">Student</option>
          <option value="Employed">Employed</option>
          <option value="Self-Employed">Self-Employed</option>
          <option value="Business Owner">Business Owner</option>
          <option value="Retired">Retired</option>
          <option value="Homemaker">Homemaker</option>
          <option value="Unemployed">Unemployed</option>
          <option value="Other">Other</option>
        </select>
      </div>
    );
  }

  if (field === "relationship") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <select
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Select</option>
          <option value="Single">Single</option>
          <option value="Married">Married</option>
          <option value="Divorced">Divorced</option>
          <option value="Widowed">Widowed</option>
          <option value="In a Relationship">In a Relationship</option>
          <option value="Prefer not to say">Prefer not to say</option>
        </select>
      </div>
    );
  }

  // For hobbies, we could use a text field with suggestions or multi-select in a more advanced implementation
  if (field === "hobbies") {
    return (
      <div>
        <label className="block text-sm text-gray-600">{label}</label>
        <textarea
          value={value || ""}
          onChange={(e) => onChange(field, e.target.value)}
          placeholder="Reading, Sports, Cooking, etc."
          className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
          rows={2}
        />
      </div>
    );
  }

  // Default input field for other types
  return (
    <div>
      <label className="block text-sm text-gray-600">{label}</label>
      <input
        type="text"
        value={value || ""}
        onChange={(e) => onChange(field, e.target.value)}
        className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>
  );
};

interface DisplayFieldProps {
  label: string;
  value: string;
}

export const DisplayField: React.FC<DisplayFieldProps> = ({ label, value }) => (
  <div>
    <label className="block text-sm text-gray-600">{label}</label>
    <p className="text-gray-900 font-medium">{value || "Not provided"}</p>
  </div>
);
