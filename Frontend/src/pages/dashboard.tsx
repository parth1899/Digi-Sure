import { useState, useEffect } from "react";
import {
  Routes,
  Route,
  useNavigate,
  useLocation,
  Navigate,
} from "react-router-dom";
import Header from "../components/Layout/Header";
import Sidebar from "../components/Layout/Sidebar";
import PersonalInfo from "../components/Pages/Info";
import Claims from "../components/Pages/Claims";
import Policies from "../components/Pages/Policies";
import Payments from "../components/Pages/Payment";
import SupportTickets from "../components/Pages/Support";
import Nominees from "../components/Pages/Nominees";
import Documents from "../components/Pages/Document";
import Security from "../components/Pages/Security";
import Reward from "../components/Pages/Rewards";
import { User } from "../types";

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const pathSegments = location.pathname.split("/");
  const currentTab = pathSegments[2] || "personal";

  const [user, setUser] = useState<User | null>(null);
  const [isComplete, setIsComplete] = useState<boolean | null>(null);
  const [hasApplications, setHasApplications] = useState<boolean>(false);

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

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const token = localStorage.getItem("token");
        const headers = {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        };

        const [userRes, completeRes] = await Promise.all([
          fetch("http://localhost:8081/dashboard/user", {
            method: "GET",
            headers,
          }),
          fetch("http://localhost:8081/dashboard/user/is-complete", {
            method: "GET",
            headers,
          }),
        ]);

        const userData = await userRes.json();
        const completeData = await completeRes.json();
        console.log("userData", userData);
        console.log("completeData", completeData);

        if (userRes.ok && userData.success) {
          setUser(userData.user);
        } else {
          console.error("Error fetching user details:", userData.message);
        }

        if (completeRes.ok && completeData.success !== undefined) {
          setIsComplete(completeData.isComplete);
          setHasApplications(completeData.hasApplications || false);
        } else {
          console.error(
            "Error fetching profile completeness:",
            completeData.message
          );
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };

    fetchUserData();
  }, []);

  if (!user || isComplete === null) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isComplete && (
          <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-yellow-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Your profile is incomplete. Please complete your profile to
                  access all features.
                </p>
                <p className="mt-2 text-sm">
                  <button
                    onClick={() => navigate("/dashboard/personal")}
                    className="font-medium text-yellow-700 hover:text-yellow-600 focus:outline-none focus:underline"
                  >
                    Complete Profile →
                  </button>
                </p>
              </div>
            </div>
          </div>
        )}
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
              <Route index element={<Navigate to="personal" replace />} />
              <Route path="personal" element={<PersonalInfo />} />
              {isComplete && (
                <>
                  <Route path="policies" element={<Policies />} />
                  {hasApplications && <Route path="claims" element={<Claims />} />}
                  <Route path="documents" element={<Documents />} />
                </>
              )}
              <Route path="payments" element={<Payments />} />
              <Route path="support" element={<SupportTickets />} />
              <Route path="nominees" element={<Nominees />} />
              <Route path="security" element={<Security />} />
              <Route path="rewards" element={<Reward />} />
              <Route
                path="*"
                element={
                  <div className="bg-white p-6 rounded-lg shadow-sm">
                    <p className="text-gray-600">
                      Select a tab to view details
                    </p>
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
