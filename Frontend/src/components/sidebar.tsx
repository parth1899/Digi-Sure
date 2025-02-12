// Sidebar.tsx
import React, { useState } from "react";
import {
  Home,
  User,
  FileText,
  ClipboardCheck,
  Settings,
  HelpCircle,
  Timer,
  ChevronDown,
  ChevronRight,
  FileSearch,
  UserCog,
  FilePlus,
  FileEdit,
  CheckSquare,
  ClockIcon,
} from "lucide-react";

interface NavItem {
  path: string;
  icon: React.ReactNode;
  label: string;
  subItems?: SubItem[];
}

interface SubItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

interface StyleTypes {
  sidebar: React.CSSProperties;
  logo: React.CSSProperties;
  nav: React.CSSProperties;
  navItem: React.CSSProperties;
  icon: React.CSSProperties;
  activeNavItem: React.CSSProperties;
  subNav: React.CSSProperties;
  subItem: React.CSSProperties;
  chevron: React.CSSProperties;
  footer: React.CSSProperties;
}

const Sidebar: React.FC = () => {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const style: StyleTypes = {
    sidebar: {
      width: "250px",
      height: "100vh",
      backgroundColor: "#1a1a1a",
      color: "#ffffff",
      padding: "20px",
      position: "fixed",
      left: 0,
      top: 0,
      display: "flex",
      flexDirection: "column",
      overflowY: "auto",
    },
    logo: {
      fontSize: "24px",
      fontWeight: "bold",
      marginBottom: "40px",
      textAlign: "center",
    },
    nav: {
      display: "flex",
      flexDirection: "column",
      flex: 1,
    },
    navItem: {
      display: "flex",
      alignItems: "center",
      padding: "12px 16px",
      marginBottom: "4px",
      textDecoration: "none",
      color: "#ffffff",
      borderRadius: "6px",
      transition: "background-color 0.2s",
      cursor: "pointer",
    },
    icon: {
      marginRight: "12px",
      minWidth: "20px",
    },
    activeNavItem: {
      backgroundColor: "#2d2d2d",
    },
    subNav: {
      marginLeft: "20px",
      display: "flex",
      flexDirection: "column",
      marginBottom: "8px",
    },
    subItem: {
      display: "flex",
      alignItems: "center",
      padding: "8px 16px",
      textDecoration: "none",
      color: "#ffffff",
      borderRadius: "6px",
      transition: "background-color 0.2s",
      fontSize: "0.9em",
    },
    chevron: {
      marginLeft: "auto",
      transition: "transform 0.2s",
    },
    footer: {
      borderTop: "1px solid #2d2d2d",
      paddingTop: "20px",
      marginTop: "auto",
    },
  };

  const navItems: NavItem[] = [
    {
      path: "/dashboard",
      icon: <Home size={20} />,
      label: "Home",
    },
    {
      path: "/dashboard/profile",
      icon: <User size={20} />,
      label: "Profile",
      subItems: [
        {
          path: "/dashboard/profile/details",
          label: "Personal Details",
          icon: <UserCog size={18} />,
        },
        {
          path: "/dashboard/profile/documents",
          label: "Documents",
          icon: <FileSearch size={18} />,
        },
      ],
    },
    {
      path: "/dashboard/apply",
      icon: <FileText size={20} />,
      label: "Apply",
      subItems: [
        {
          path: "/dashboard/apply/new",
          label: "New Application",
          icon: <FilePlus size={18} />,
        },
        {
          path: "/dashboard/apply/draft",
          label: "Draft Applications",
          icon: <FileEdit size={18} />,
        },
      ],
    },
    {
      path: "/dashboard/claim",
      icon: <ClipboardCheck size={20} />,
      label: "Claim",
      subItems: [
        {
          path: "/dashboard/claim/submit",
          label: "Submit Claim",
          icon: <CheckSquare size={18} />,
        },
        {
          path: "/dashboard/claim/history",
          label: "Claim History",
          icon: <ClockIcon size={18} />,
        },
      ],
    },
    {
      path: "/dashboard/tracker",
      icon: <Timer size={20} />,
      label: "Application Tracker",
    },
    {
      path: "/dashboard/settings",
      icon: <Settings size={20} />,
      label: "Settings",
    },
    {
      path: "/dashboard/help",
      icon: <HelpCircle size={20} />,
      label: "Help",
    },
  ];

  const toggleExpand = (label: string) => {
    setExpandedItems((prev) =>
      prev.includes(label)
        ? prev.filter((item) => item !== label)
        : [...prev, label]
    );
  };

  const isActivePath = (path: string): boolean => {
    return window.location.pathname === path;
  };

  return (
    <div style={style.sidebar}>
      <div style={style.logo}>Dashboard</div>

      <nav style={style.nav}>
        {navItems.map((item) => (
          <div key={item.path}>
            <div
              onClick={() =>
                item.subItems ? toggleExpand(item.label) : undefined
              }
              style={{
                ...style.navItem,
                ...(isActivePath(item.path) ? style.activeNavItem : {}),
              }}
            >
              <span style={style.icon}>{item.icon}</span>
              {item.label}
              {item.subItems && (
                <span style={style.chevron}>
                  {expandedItems.includes(item.label) ? (
                    <ChevronDown size={16} />
                  ) : (
                    <ChevronRight size={16} />
                  )}
                </span>
              )}
            </div>

            {item.subItems && expandedItems.includes(item.label) && (
              <div style={style.subNav}>
                {item.subItems.map((subItem) => (
                  <a
                    key={subItem.path}
                    href={subItem.path}
                    style={{
                      ...style.subItem,
                      ...(isActivePath(subItem.path)
                        ? style.activeNavItem
                        : {}),
                    }}
                  >
                    <span style={style.icon}>{subItem.icon}</span>
                    {subItem.label}
                  </a>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
