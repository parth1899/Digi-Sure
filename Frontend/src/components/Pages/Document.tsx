import React, { useState } from "react";
import { FileText, User, ClipboardList, X, Upload, File } from "lucide-react";
import { Document } from "../../types";
// import { Document, UploadFormData } from "../../types";

type UploadFormData = {
  documentType: string;
  documentName: string;
  file: File | null;
};

// const DOCUMENT_TYPES = ['Policy', 'KYC', 'Medical', 'Claim', 'Other'] as const;
const DOCUMENT_TYPES = ["Policy", "KYC", "Medical", "Claim", "Other"] as const;

const documents: Document[] = [
  {
    id: "1",
    name: "Policy Documents",
    icon: FileText,
    count: 3,
    type: "Policy",
    uploadedOn: new Date("2024-03-10"),
    size: 1024,
  },
  {
    id: "2",
    name: "KYC Documents",
    icon: User,
    count: 2,
    type: "KYC",
    uploadedOn: new Date("2024-03-09"),
    size: 2048,
  },
  {
    id: "3",
    name: "Medical Reports",
    icon: FileText,
    count: 1,
    type: "Medical",
    uploadedOn: new Date("2024-03-08"),
    size: 3072,
  },
  {
    id: "4",
    name: "Claim Documents",
    icon: ClipboardList,
    count: 1,
    type: "Claim",
    uploadedOn: new Date("2024-03-07"),
    size: 512,
  },
];

const Documents: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [documentsList, setDocumentsList] = useState<Document[]>(documents);
  const [dragActive, setDragActive] = useState(false);
  const [formData, setFormData] = useState<UploadFormData>({
    documentType: "",
    documentName: "",
    file: null,
  });

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (file: File) => {
    if (file.type === "application/pdf" || file.type.startsWith("image/")) {
      setFormData((prev) => ({ ...prev, file }));
    } else {
      alert("Please upload only PDF or image files");
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.documentType || !formData.file) return;

    const newDocument: Document = {
      id: Date.now().toString(),
      name: formData.documentName || formData.file.name,
      type: formData.documentType,
      icon: FileText,
      count: 1,
      uploadedOn: new Date(),
      size: formData.file.size,
    };

    setDocumentsList((prev) => [...prev, newDocument]);
    setIsModalOpen(false);
    setFormData({ documentType: "", documentName: "", file: null });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Documents Vault</h3>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            Upload Document
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documentsList.map((doc) => (
            <div
              key={doc.id}
              className="border rounded-lg p-4 hover:border-blue-500 transition-colors"
            >
              <div className="flex items-center space-x-3">
                {React.createElement(doc.icon)}
                <div className="flex-1">
                  <p className="font-medium">{doc.name}</p>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <span>
                      {doc.count} document{doc.count !== 1 ? "s" : ""}
                    </span>
                    {doc.size && <span>• {formatFileSize(doc.size)}</span>}
                  </div>
                  {doc.uploadedOn && (
                    <p className="text-xs text-gray-400 mt-1">
                      Uploaded on {doc.uploadedOn.toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-md flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md m-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Upload Document</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Type
                </label>
                <select
                  required
                  value={formData.documentType}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      documentType: e.target.value as Document["type"],
                    }))
                  }
                  className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                >
                  <option value="">Select type</option>
                  {DOCUMENT_TYPES.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Name (Optional)
                </label>
                <input
                  type="text"
                  value={formData.documentName}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      documentName: e.target.value,
                    }))
                  }
                  className="w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  placeholder="Enter custom name"
                />
              </div>

              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors
                  ${
                    dragActive
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-300"
                  }
                  ${formData.file ? "bg-green-50" : ""}`}
              >
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg"
                  onChange={handleFileInput}
                  className="hidden"
                  id="file-upload"
                />
                <label
                  htmlFor="file-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  {formData.file ? (
                    <>
                      <File className="w-8 h-8 text-green-500 mb-2" />
                      <p className="text-sm text-green-600 font-medium">
                        {formData.file.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatFileSize(formData.file.size)}
                      </p>
                    </>
                  ) : (
                    <>
                      <Upload className="w-8 h-8 text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600">
                        Drag & drop your file here or{" "}
                        <span className="text-blue-500">browse</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        Supports PDF, JPG, JPEG
                      </p>
                    </>
                  )}
                </label>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  disabled={!formData.documentType || !formData.file}
                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 
                    disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Upload
                </button>
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg 
                    hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Documents;
