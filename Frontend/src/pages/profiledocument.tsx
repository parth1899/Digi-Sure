import React, { useState, useRef } from "react";
import { Upload, X } from "lucide-react";

interface FileUploadState {
  file: File | null;
  preview: string | null;
  error: string | null;
  isUploading: boolean;
  isSuccess: boolean;
}

const Profile: React.FC = () => {
  const [uploadState, setUploadState] = useState<FileUploadState>({
    file: null,
    preview: null,
    error: null,
    isUploading: false,
    isSuccess: false,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    // Validate file type
    if (!["application/pdf", "image/jpeg", "image/png"].includes(file.type)) {
      setUploadState((prev) => ({
        ...prev,
        error: "Please upload a PDF, JPEG, or PNG file",
      }));
      return;
    }

    // Validate file size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setUploadState((prev) => ({
        ...prev,
        error: "File size should be less than 5MB",
      }));
      return;
    }

    setUploadState({
      file,
      preview: URL.createObjectURL(file),
      error: null,
      isUploading: false,
      isSuccess: false,
    });
  };

  const handleUpload = async () => {
    if (!uploadState.file) return;

    setUploadState((prev) => ({ ...prev, isUploading: true, error: null }));

    try {
      const formData = new FormData();
      formData.append("file", uploadState.file);

      const response = await fetch(
        "http://localhost:8080/docs/upload-aadhaar-card",
        {
          method: "POST",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"), // Assuming token is stored in localStorage
          },
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      await response.json();

      setUploadState((prev) => ({
        ...prev,
        isUploading: false,
        isSuccess: true,
      }));
    } catch (error) {
      setUploadState((prev) => ({
        ...prev,
        isUploading: false,
        error: error instanceof Error ? error.message : "Upload failed",
      }));
    }
  };

  const clearFile = () => {
    if (uploadState.preview) {
      URL.revokeObjectURL(uploadState.preview);
    }
    setUploadState({
      file: null,
      preview: null,
      error: null,
      isUploading: false,
      isSuccess: false,
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const style: Record<string, React.CSSProperties> = {
    container: {
      padding: "24px",
      maxWidth: "800px",
      margin: "0 auto",
    },
    header: {
      marginBottom: "24px",
    },
    uploadSection: {
      border: "2px dashed #ccc",
      borderRadius: "8px",
      padding: "32px",
      textAlign: "center",
      backgroundColor: "#f9f9f9",
      cursor: "pointer",
      transition: "border-color 0.2s",
      marginBottom: "20px",
    },
    fileInput: {
      display: "none",
    },
    uploadIcon: {
      marginBottom: "12px",
    },
    fileName: {
      marginTop: "12px",
      wordBreak: "break-all",
    },
    button: {
      backgroundColor: "#2563eb",
      color: "white",
      padding: "8px 16px",
      borderRadius: "6px",
      border: "none",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      gap: "8px",
    },
    clearButton: {
      backgroundColor: "#dc2626",
      marginLeft: "8px",
    },
    buttonDisabled: {
      opacity: 0.5,
      cursor: "not-allowed",
    },
    error: {
      color: "#dc2626",
      marginTop: "12px",
    },
    success: {
      color: "#16a34a",
      marginTop: "12px",
    },
  };

  return (
    <div style={style.container}>
      <div style={style.header}>
        <h1>Profile</h1>
        <p>Upload your Aadhaar card for verification</p>
      </div>

      <div
        style={style.uploadSection}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={handleFileSelect}
          style={style.fileInput}
        />

        {!uploadState.file ? (
          <>
            <Upload size={48} style={style.uploadIcon} />
            <p>Click or drag and drop to upload your Aadhaar card</p>
            <p style={{ fontSize: "0.875rem", color: "#666" }}>
              Supported formats: PDF, JPEG, PNG (max 5MB)
            </p>
          </>
        ) : (
          <div style={style.fileName}>
            <p>
              <strong>Selected file:</strong> {uploadState.file.name}
            </p>
          </div>
        )}
      </div>

      {uploadState.error && <p style={style.error}>{uploadState.error}</p>}

      {uploadState.isSuccess && (
        <p style={style.success}>File uploaded successfully!</p>
      )}

      {uploadState.file && !uploadState.isSuccess && (
        <button
          onClick={handleUpload}
          style={{
            ...style.button,
            ...(uploadState.isUploading ? style.buttonDisabled : {}),
          }}
          disabled={uploadState.isUploading}
        >
          <Upload size={16} />
          {uploadState.isUploading ? "Uploading..." : "Upload Aadhaar Card"}
        </button>
      )}

      {uploadState.file && (
        <button
          onClick={clearFile}
          style={{ ...style.button, ...style.clearButton }}
        >
          <X size={16} />
          Clear
        </button>
      )}
    </div>
  );
};

export default Profile;
