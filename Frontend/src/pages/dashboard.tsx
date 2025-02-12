// Dashboard.tsx
import React, { ReactNode } from "react";
import Sidebar from "../components/sidebar";

interface DashboardProps {
  children?: ReactNode;
}

interface StyleTypes {
  layout: React.CSSProperties;
  main: React.CSSProperties;
}

const Dashboard: React.FC<DashboardProps> = ({ children }) => {
  const style: StyleTypes = {
    layout: {
      display: "flex",
    },
    main: {
      marginLeft: "250px",
      padding: "20px",
      width: "100%",
    },
  };

  return (
    <div style={style.layout}>
      <Sidebar />
      <main style={style.main}>
        <h1>Dashboard</h1>
        {children}
      </main>
    </div>
  );
};

export default Dashboard;
