// pages/Dashboard.tsx
import React from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/sidebar";

interface StyleTypes {
  layout: React.CSSProperties;
  main: React.CSSProperties;
}

const Dashboard: React.FC = () => {
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
        <Outlet />
      </main>
    </div>
  );
};

export default Dashboard;
