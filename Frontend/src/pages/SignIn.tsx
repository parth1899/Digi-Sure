import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/auth.css";

const SignIn = () => {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Sign-in data:", formData);
    // Add your backend logic for sign-in
    navigate("/dashboard"); // Redirect after successful login
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
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={formData.username}
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
