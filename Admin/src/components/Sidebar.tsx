import { NavLink } from "react-router-dom";
import { Home, FileText, AlertCircle, LogOut } from "lucide-react";

const Sidebar = () => {
  return (
    <div className="h-screen w-48 bg-white border-r border-gray-200 text-gray-900 p-4">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-blue-600">Insurance Admin</h1>
      </div>

      <nav className="space-y-3">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center space-x-2 p-2 rounded-lg transition-colors ${
              isActive ? "bg-blue-50 text-blue-600" : "hover:bg-gray-50"
            }`
          }
        >
          <Home size={18} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/policies"
          className={({ isActive }) =>
            `flex items-center space-x-2 p-2 rounded-lg transition-colors ${
              isActive ? "bg-blue-50 text-blue-600" : "hover:bg-gray-50"
            }`
          }
        >
          <FileText size={18} />
          <span>Policies</span>
        </NavLink>

        <NavLink
          to="/claims"
          className={({ isActive }) =>
            `flex items-center space-x-2 p-2 rounded-lg transition-colors ${
              isActive ? "bg-blue-50 text-blue-600" : "hover:bg-gray-50"
            }`
          }
        >
          <AlertCircle size={18} />
          <span>Claims</span>
        </NavLink>
      </nav>

      <div className="absolute bottom-4 left-4">
        <button className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors">
          <LogOut size={18} />
          <span>Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
