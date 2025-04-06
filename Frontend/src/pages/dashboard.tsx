import { Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";
import Header from "../components/Layout/Header";
import Sidebar from "../components/Layout/Sidebar";
import PersonalInfo from "../components/Pages/Info";
import Claims from "../components/Pages/Claims";
import Policies from "../components/Pages/Policies";
import Payments from "../components/Pages/Payment";
import { User } from "../types";
import SupportTickets from "../components/Pages/Support";
import Nominees from "../components/Pages/Nominees";
import Documents from "../components/Pages/Document";
import Security from "../components/Pages/Security";
import Reward from "../components/Pages/Rewards";

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Extract the current tab from the URL. Defaults to "personal" if no tab is provided.
  const pathSegments = location.pathname.split("/");
  const currentTab = pathSegments[2] || "personal";

  const getTabTitle = () => {
    switch (currentTab) {
      case "personal":
        return {
          title: "My Profile",
          subtitle: "Manage your insurance profile and policies",
        };
      case "policies":
        return {
          title: "Insurance Policies",
          subtitle: "View and manage your active insurance policies",
        };
      case "claims":
        return {
          title: "Claims Management",
          subtitle: "Track and manage your insurance claims",
        };
      case "payments":
        return {
          title: "Payments & Billing",
          subtitle: "Manage your payment methods and view transactions",
        };
      case "support":
        return {
          title: "Support Tickets",
          subtitle: "Get help and track your support requests",
        };
      case "nominees":
        return {
          title: "Nominee Management",
          subtitle: "Add and manage your policy nominees",
        };
      case "documents":
        return {
          title: "My Documents",
          subtitle: "Access and download your insurance documents",
        };
      case "security":
        return {
          title: "Security Settings",
          subtitle: "Manage your account security and privacy preferences",
        };
      case "rewards":
        return {
          title: "Rewards & Benefits",
          subtitle: "View your reward points and exclusive member benefits",
        };
      default:
        return {
          title: "Dashboard",
          subtitle: "Select a tab to view details",
        };
    }
  };

  const user: User = {
    name: "",
    customerId: "SBI87654321",
    email: "rajesh.kumar@email.com",
    mobile: "+91 98765 43210",
    address: "123, Park Street, Mumbai",
    otherDetails: {
      sex: undefined,
      dob: undefined,
      education_level: "",
      occupation: "",
      hobbies: "",
      relationship: "",
    },
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-8">
          <Sidebar
            activeTab={currentTab}
            setActiveTab={(tab) => navigate(`/dashboard/${tab}`)}
          />
          <div className="flex-1">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                {getTabTitle().title}
              </h1>
              <p className="text-sm text-gray-600">{getTabTitle().subtitle}</p>
            </div>
            <Routes>
              {/* When the user lands on /dashboard, redirect to /dashboard/personal */}
              <Route index element={<Navigate to="personal" replace />} />
              <Route path="personal" element={<PersonalInfo />} />
              <Route path="policies" element={<Policies />} />
              <Route path="claims" element={<Claims />} />
              <Route path="payments" element={<Payments />} />
              <Route path="support" element={<SupportTickets />} />
              <Route path="nominees" element={<Nominees />} />
              <Route path="documents" element={<Documents />} />
              <Route path="security" element={<Security />} />
              <Route path="rewards" element={<Reward />} />
              <Route
                path="*"
                element={
                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <p className="text-gray-600">Select a tab to view details</p>
                  </div>
                }
              />
            </Routes>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
