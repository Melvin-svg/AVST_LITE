import React, { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function Dashboard() {
  const { token, user } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .challenges(token)
      .then(setChallenges)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const solved = useMemo(() => challenges.filter((c) => c.solved), [challenges]);
  const totalPoints = useMemo(
    () => solved.reduce((sum, c) => sum + (c.points || 0), 0),
    [solved]
  );
  const nextUp = useMemo(() => challenges.find((c) => !c.solved), [challenges]);
  const completionPct = challenges.length
    ? Math.round((solved.length / challenges.length) * 100)
    : 0;

  // Breakdown by category
  const categories = useMemo(() => {
    const map = {};
    challenges.forEach((c) => {
      const cat = c.category || "General";
      if (!map[cat]) map[cat] = { total: 0, solved: 0 };
      map[cat].total += 1;
      if (c.solved) map[cat].solved += 1;
    });
    return Object.entries(map).map(([name, data]) => ({
      name,
      ...data,
      pct: Math.round((data.solved / data.total) * 100),
    }));
  }, [challenges]);

  return (
    <div className="page dashboard-page">
      {/* Telemetry Bar */}
      <div className="telemetry-bar">
        <div className="telemetry-item">
          <span className="live-dot-pulse"></span>
          <span className="telemetry-label">SECURITY SOC:</span>
          <span className="telemetry-val text-accent">ACTIVE DEFENSE</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">CLEARANCE:</span>
          <span className="telemetry-val">LEVEL 2 (AGENT)</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">SYSTEM TIME:</span>
          <span className="telemetry-val">{new Date().toISOString().split("T")[0]} UTC</span>
        </div>
      </div>

      {/* Hero Welcome Banner */}
      <div className="dashboard-hero">
        <div className="hero-content">
          <div className="hero-pill-badge">OPERATIONS HUB</div>
          <h1>Welcome, <span className="hero-gradient-text">{user?.name || "Agent"}</span></h1>
          <p className="subtitle">
            {loading
              ? "Decrypting training progress and mission status..."
              : solved.length === 0
              ? "Welcome to your security playground. Begin your first mission below."
              : `Commendable work, Agent. You have amassed ${totalPoints} points across ${solved.length} completed operation${solved.length === 1 ? "" : "s"}.`}
          </p>

          {/* Progress Bar */}
          <div className="hero-progress-container">
            <div className="hero-progress-meta">
              <span>Overall Mission Completion</span>
              <strong>{completionPct}% ({solved.length}/{challenges.length})</strong>
            </div>
            <div className="hero-progress-track">
              <div
                className="hero-progress-fill"
                style={{ width: `${completionPct}%` }}
              ></div>
            </div>
          </div>
        </div>

        {nextUp && (
          <div className="next-mission-card">
            <div className="mission-card-badge">NEXT OBJECTIVE</div>
            <h3>{nextUp.title}</h3>
            <p className="mission-meta">
              <span className="category-tag">{nextUp.category}</span>
              <span className={`difficulty-badge diff-${nextUp.difficulty}`}>{nextUp.difficulty}</span>
              <span className="points-pill">+{nextUp.points} pts</span>
            </p>
            <Link to={`/challenges/${nextUp.challenge_id}`} className="mission-launch-btn">
              <span>Engage Target</span>
              <span className="btn-arrow">➔</span>
            </Link>
          </div>
        )}
      </div>

      {/* Metric Cards */}
      <div className="stat-cards">
        <div className="stat-card">
          <div className="stat-card-icon">🎯</div>
          <div className="stat-info">
            <span className="stat-value">{challenges.length}</span>
            <span className="stat-label">Total Missions</span>
          </div>
        </div>
        <div className="stat-card accent">
          <div className="stat-card-icon">🏆</div>
          <div className="stat-info">
            <span className="stat-value">{solved.length}</span>
            <span className="stat-label">Objectives Neutralized</span>
          </div>
        </div>
        <div className="stat-card points-card">
          <div className="stat-card-icon">⚡</div>
          <div className="stat-info">
            <span className="stat-value">{totalPoints}</span>
            <span className="stat-label">Score / Points</span>
          </div>
        </div>
        <div className="stat-card rank-card">
          <div className="stat-card-icon">🎖️</div>
          <div className="stat-info">
            <span className="stat-value">Tier 1</span>
            <span className="stat-label">Operative Rank</span>
          </div>
        </div>
      </div>

      {/* Category Breakdown */}
      {categories.length > 0 && (
        <div className="category-breakdown-panel">
          <h2 className="section-title">Specialization Readiness</h2>
          <div className="category-progress-grid">
            {categories.map((cat) => (
              <div key={cat.name} className="cat-progress-card">
                <div className="cat-progress-head">
                  <span className="cat-name">{cat.name}</span>
                  <span className="cat-score">{cat.solved}/{cat.total}</span>
                </div>
                <div className="cat-progress-track">
                  <div
                    className="cat-progress-fill"
                    style={{ width: `${cat.pct}%` }}
                  ></div>
                </div>
                <div className="cat-pct-label">{cat.pct}% Complete</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation Command Grid */}
      <h2 className="section-title">Navigation Deck</h2>
      <div className="card-grid">
        <Link to="/challenges" className="nav-card cyber-card">
          <div className="nav-card-top">
            <span className="nav-card-icon">🏴</span>
            <span className="card-badge-sub">Labs</span>
          </div>
          <h3>CTF Challenges</h3>
          <p>
            Exploit vulnerabilities across Web Security, Cryptography, Forensics, and
            Reverse Engineering.
          </p>
          <span className="card-cta-link">Deploy to Arena ➔</span>
        </Link>

        <Link to="/cve" className="nav-card cyber-card">
          <div className="nav-card-top">
            <span className="nav-card-icon">🛡️</span>
            <span className="card-badge-sub live">Realtime</span>
          </div>
          <h3>CVE Threat Intelligence</h3>
          <p>
            Study live real-world zero-days, CISA ransomware vectors, and vulnerability mitigation.
          </p>
          <span className="card-cta-link">Access Feed ➔</span>
        </Link>

        <Link to="/leaderboard" className="nav-card cyber-card">
          <div className="nav-card-top">
            <span className="nav-card-icon">🏆</span>
            <span className="card-badge-sub">Global</span>
          </div>
          <h3>Operative Leaderboard</h3>
          <p>
            Analyze rankings, compare execution times, and rise to the apex of the CTF roster.
          </p>
          <span className="card-cta-link">Inspect Standings ➔</span>
        </Link>
      </div>
    </div>
  );
}
