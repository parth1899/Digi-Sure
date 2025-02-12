import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/auth.css";

interface FormData {
  email: string;
  name: string;
  surname: string;
  password: string;
}
const SignUp = () => {
  const [formData, setFormData] = useState<FormData>({
    email: "",
    name: "",
    surname: "",
    password: "",
  });
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError(""); // Clear any previous errors when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        "http://localhost:8080/auth/register",
        formData
      );

      if (response.status === 200 || response.status === 201) {
        localStorage.setItem("token", response.data.token);
        console.log("Registration successful!");
        navigate("/signin");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(
          err.response?.data?.message ||
            "Registration failed. Please try again."
        );
      } else {
        setError("An unexpected error occurred.");
      }
      console.error("Registration error:", err);
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
        <h2 style={{ color: "#007bff" }}>Sign Up</h2>
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
            placeholder="E-mail"
            value={formData.email}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="name"
            placeholder="First Name"
            value={formData.name}
            onChange={handleChange}
            required
          />
          <input
            type="text"
            name="surname"
            placeholder="Last Name"
            value={formData.surname}
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
            minLength={8}
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
            Sign Up
          </button>
        </form>
        <div className="footer">
          Already have an account? <a href="/signin">Sign In</a>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
