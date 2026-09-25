import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const CATEGORIES = [
  { label: "All", icon: "🌐" },
  { label: "Web Security", icon: "🌐" },
  { label: "Cryptography", icon: "🔐" },
  { label: "Forensics", icon: "🔍" },
  { label: "Reverse Engineering", icon: "⚙️" },
];

const DIFFICULTIES = ["All", "Easy", "Medium", "Hard", "Insane"];

export default function Challenges() {
  const { token } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("All");
  const [difficulty, setDifficulty] = useState("All");
  const [statusFilter, setStatusFilter] = useState("all"); // 'all', 'unsolved', 'solved'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .challenges(token)
      .then(setChallenges)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const filtered = useMemo(() => {
    return challenges.filter((c) => {
      // Category filter
      if (category !== "All" && c.category !== category) return false;
      // Difficulty filter
      if (difficulty !== "All" && c.difficulty !== difficulty) return false;
      // Status filter
      if (statusFilter === "solved" && !c.solved) return false;
      if (statusFilter === "unsolved" && c.solved) return false;
      // Search query
      if (search.trim()) {
        const q = search.toLowerCase();
        const matchTitle = c.title?.toLowerCase().includes(q);
        const matchDesc = c.description?.toLowerCase().includes(q);
        const matchCat = c.category?.toLowerCase().includes(q);
        if (!matchTitle && !matchDesc && !matchCat) return false;
      }
      return true;
    });
  }, [challenges, category, difficulty, statusFilter, search]);

  const solvedCount = challenges.filter((c) => c.solved).length;
  const pctSolved = challenges.length
    ? Math.round((solvedCount / challenges.length) * 100)
    : 0;

  return (
    <div className="page challenges-page">
      {/* Header with Circular / Pill Progress Indicator */}
      <div className="page-header">
        <div>
          <div className="header-eyebrow">TACTICAL CTF ARENA</div>
          <h1>Security Challenges</h1>
          <p className="subtitle">
            {challenges.length > 0
              ? `${solvedCount} of ${challenges.length} objectives neutralized (${pctSolved}% clearance)`
              : "Synchronizing tactical simulation deck..."}
          </p>
        </div>

        {challenges.length > 0 && (
          <div className="challenge-summary-badge">
            <div className="progress-ring-wrap">
              <div
                className="progress-ring"
                style={{ "--pct": `${pctSolved}%` }}
              >
                <span>{pctSolved}%</span>
              </div>
            </div>
            <div className="summary-stat-text">
              <span className="summary-val">{challenges.length - solvedCount} Remaining</span>
              <span className="summary-label">Active Targets</span>
            </div>
          </div>
        )}
      </div>

      {/* Filter and Search Bar Controls */}
      <div className="challenges-control-deck">
        <div className="search-bar-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            className="challenge-search-input"
            placeholder="Search challenges by keyword, vulnerability, or protocol..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="clear-search-btn" onClick={() => setSearch("")}>
              ✕
            </button>
          )}
        </div>

        <div className="filter-groups">
          {/* Categories */}
          <div className="filter-bar">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.label}
                className={cat.label === category ? "filter-btn active" : "filter-btn"}
                onClick={() => setCategory(cat.label)}
              >
                <span className="cat-btn-icon">{cat.icon}</span>
                <span>{cat.label}</span>
              </button>
            ))}
          </div>

          <div className="filter-secondary-row">
            {/* Difficulties */}
            <div className="filter-bar">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  className={
                    d === difficulty
                      ? `filter-btn diff-btn active diff-${d}`
                      : `filter-btn diff-btn diff-${d}`
                  }
                  onClick={() => setDifficulty(d)}
                >
                  {d}
                </button>
              ))}
            </div>

            {/* Status Segmented Control */}
            <div className="status-filter-toggle">
              <button
                className={`status-btn ${statusFilter === "all" ? "active" : ""}`}
                onClick={() => setStatusFilter("all")}
              >
                All
              </button>
              <button
                className={`status-btn ${statusFilter === "unsolved" ? "active" : ""}`}
                onClick={() => setStatusFilter("unsolved")}
              >
                Unsolved
              </button>
              <button
                className={`status-btn ${statusFilter === "solved" ? "active" : ""}`}
                onClick={() => setStatusFilter("solved")}
              >
                Solved
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Empty State */}
      {!loading && filtered.length === 0 && (
        <div className="challenges-empty-state">
          <span className="empty-state-icon">📡</span>
          <h3>No matching targets detected</h3>
          <p>Try modifying your keyword query or resetting your difficulty filters.</p>
          <button
            className="reset-filters-btn"
            onClick={() => {
              setSearch("");
              setCategory("All");
              setDifficulty("All");
              setStatusFilter("all");
            }}
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Grid of Challenge Cards */}
      <div className="challenge-grid">
        {filtered.map((c) => (
          <Link
            key={c.challenge_id}
            to={`/challenges/${c.challenge_id}`}
            className={`challenge-card ${c.solved ? "is-solved" : ""}`}
          >
            <div className="card-cyber-accent"></div>
            <div className="challenge-card-top">
              <span className="category-tag">{c.category}</span>
              <span className={`difficulty-badge diff-${c.difficulty}`}>
                {c.difficulty}
              </span>
            </div>

            <h3>{c.title}</h3>

            <p className="challenge-short-desc">
              {c.description
                ? c.description.slice(0, 90) + (c.description.length > 90 ? "..." : "")
                : "Examine challenge directives, uncover vulnerabilities, and extract the flag."}
            </p>

            <div className="flag-format-hint">
              <span>Flag: </span>
              <code>{c.flag_format}</code>
            </div>

            <div className="challenge-card-footer">
              <span className="points-pill">+{c.points} pts</span>
              {c.solved ? (
                <span className="solved-tag">
                  <span className="check-icon">✓</span> Solved
                </span>
              ) : (
                <span className="card-action-cue">Engage Target ➔</span>
              )}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
