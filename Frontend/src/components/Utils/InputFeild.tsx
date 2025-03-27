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
}) => (
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
