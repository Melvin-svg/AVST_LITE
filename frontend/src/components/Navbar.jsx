import React from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const LINKS = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/challenges", label: "Challenges" },
  { to: "/cve", label: "CVE Learning" },
  { to: "/leaderboard", label: "Leaderboard" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <NavLink to="/dashboard">
          <span className="brand-mark">AVST</span>
          <span className="brand-sub">Lite</span>
        </NavLink>
      </div>
      <div className="navbar-links">
        {LINKS.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            {l.label}
          </NavLink>
        ))}
      </div>
      <div className="navbar-user">
        <span className="avatar">{user.name?.[0]?.toUpperCase() || "?"}</span>
        <span className="user-name">{user.name}</span>
        <button
          className="logout-btn"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
