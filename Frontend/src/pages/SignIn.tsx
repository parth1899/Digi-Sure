import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/auth.css";

interface FormData {
  email: string;
  password: string;
}
const SignIn = () => {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8080/auth/sign-in",
        formData
      );

      if (response.status === 200) {
        localStorage.setItem("token", response.data.token);
        console.log("Sign-in successful!");
        navigate("/dashboard");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.message || "Invalid email or password.");
      } else {
        setError("An unexpected error occurred.");
      }
      console.error("Sign-in error:", err);
    }
  };

  return (
    <div>
      <video autoPlay muted loop className="video-background">
        <source src="assets/bg_video.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <div className="bank-title">State Bank of India</div>
      <div className="auth-container">
        <img src="assets/SBI-Logo.jpg" alt="Bank Logo" className="logo" />
        <h2 style={{ color: "#007bff" }}>Sign In</h2>
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          {error && <div className="error-message">{error}</div>}
          <input
            type="email"
            name="email"
            placeholder="E-Mail"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
          <button
            type="submit"
            style={{
              backgroundColor: "#007bff",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              padding: "10px",
              cursor: "pointer",
            }}
          >
            Sign In
          </button>
        </form>
        <div className="footer">
          Don't have an account? <a href="/">Sign Up</a>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
