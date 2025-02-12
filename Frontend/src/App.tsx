import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/SignIn";
import Dashboard from "./pages/dashboard";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignUp />} />
        <Route path="/signin" element={<SignIn />} />
        <Route
          path="/dashboard"
          element={
            <Dashboard>
              {/* Your dashboard content here */}
              <div>Welcome to your dashboard!</div>
            </Dashboard>
          }
        />{" "}
      </Routes>
    </Router>
  );
};

export default App;
