import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: "⌘" },
  { to: "/challenges", label: "Challenges", icon: "⚡" },
  { to: "/cve", label: "CVE Intel", icon: "🛡️" },
  { to: "/leaderboard", label: "Leaderboard", icon: "🏆" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <NavLink to="/dashboard">
          <div className="brand-logo">
            <span className="brand-glyph">◆</span>
            <span className="brand-mark">AVST</span>
            <span className="brand-sub">Lite</span>
          </div>
        </NavLink>
      </div>
      <div className="navbar-links">
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            <span className="nav-link-icon">{l.icon}</span>
            <span>{l.label}</span>
          </NavLink>
        ))}
      </div>
      <div className="navbar-user">
        <div className="avatar-ring">
          <span className="avatar">{user.name?.[0]?.toUpperCase() || "?"}</span>
        </div>
        <div className="user-info">
          <span className="user-name">{user.name}</span>
          <span className="user-role">Trainee</span>
        </div>
        <button
          className="logout-btn"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          <span className="logout-icon">⏻</span>
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
}
