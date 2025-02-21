import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import AdminHome from './pages/AdminHome';
import AdminPolicies from './pages/AdminPolicies';
import AdminClaims from './pages/AdminClaims';

function App() {
  return (
    <Router>
      <div className="flex bg-white text-gray-900 min-h-screen">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<AdminHome />} />
            <Route path="/policies" element={<AdminPolicies />} />
            <Route path="/claims" element={<AdminClaims />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;