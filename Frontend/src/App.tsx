import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignUp from "./pages/SignUp";
import SignIn from "./pages/SignIn";
import Dashboard from "./pages/dashboard";
import Profile from "./pages/profiledocument";
import Apply from "./pages/apply";

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignUp />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/dashboard" element={<Dashboard />}>
          <Route index element={<div>Welcome to Dashboard</div>} />
          <Route path="profile/documents" element={<Profile />} />
          <Route path="apply/new" element={<Apply />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;
