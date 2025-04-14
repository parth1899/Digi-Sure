import React, { useState } from "react";

const UploadFiles = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState("policy");
  const [message, setMessage] = useState<string | null>(null);
  interface ExtractedData {
    [key: string]: string | number | null;
  }

  const [extractedData, setExtractedData] = useState<ExtractedData | null>(
    null
  );

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch(
        `http://localhost:8081/ocr/extract_${uploadType}`,
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Failed to upload file.");
      }

      const data = await response.json();
      setExtractedData(data);
      setMessage(
        "File uploaded successfully. You can now edit the extracted data."
      );
    } catch (error) {
      setMessage(
        `Error: ${
          error instanceof Error ? error.message : "Unknown error occurred"
        }`
      );
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch(
        `http://localhost:8081/update_${uploadType}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(extractedData),
        }
      );
      console.log(response);

      if (!response.ok) {
        throw new Error("Failed to submit updated data.");
      }

      setMessage("Data submitted successfully.");
    } catch (error) {
      setMessage(
        `Error: ${
          error instanceof Error ? error.message : "Unknown error occurred"
        }`
      );
    }
  };

  const handleFieldChange = (field: string, value: string | number | null) => {
    setExtractedData((prevData: ExtractedData | null) => ({
      ...prevData,
      [field]: value,
    }));
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Upload Files</h1>
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select File Type
          </label>
          <select
            value={uploadType}
            onChange={(e) => setUploadType(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="policy">Policy</option>
            <option value="claim">Claim</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload File
          </label>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
        </div>

        <button
          onClick={handleUpload}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Upload
        </button>

        {message && (
          <div className="mt-4 text-sm text-gray-700 bg-gray-100 p-4 rounded">
            {message}
          </div>
        )}
      </div>

      {extractedData && (
        <div className="mt-8 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Edit Extracted Data
          </h2>
          {Object.keys(extractedData).map((field) => (
            <div key={field} className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {field}
              </label>
              <input
                type="text"
                value={extractedData[field] || ""}
                onChange={(e) => handleFieldChange(field, e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>
          ))}
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Submit
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadFiles;
