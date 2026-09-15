import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function Dashboard() {
  const { token, user } = useAuth();
  const [challenges, setChallenges] = useState([]);

  useEffect(() => {
    api.challenges(token).then(setChallenges).catch(() => {});
  }, [token]);

  const solved = challenges.filter((c) => c.solved);
  const totalPoints = solved.reduce((sum, c) => sum + c.points, 0);

  return (
    <div className="page">
      <h1>Welcome back, {user?.name}</h1>
      <div className="stat-cards">
        <div className="stat-card">
          <span className="stat-value">{challenges.length}</span>
          <span className="stat-label">Total Challenges</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{solved.length}</span>
          <span className="stat-label">Completed</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{totalPoints}</span>
          <span className="stat-label">Points Earned</span>
        </div>
      </div>

      <h2>Continue Learning</h2>
      <div className="card-grid">
        <Link to="/challenges" className="nav-card">
          <h3>CTF Challenges</h3>
          <p>Solve Web, Crypto, Forensics and Reverse Engineering challenges.</p>
        </Link>
        <Link to="/cve" className="nav-card">
          <h3>CVE Learning</h3>
          <p>Read about real-world vulnerabilities before you attempt labs.</p>
        </Link>
        <Link to="/leaderboard" className="nav-card">
          <h3>Leaderboard</h3>
          <p>See how you rank against classmates.</p>
        </Link>
      </div>
    </div>
  );
}
