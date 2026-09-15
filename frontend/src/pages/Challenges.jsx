import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const CATEGORIES = ["All", "Web Security", "Cryptography", "Forensics", "Reverse Engineering"];
const DIFFICULTIES = ["All", "Easy", "Medium", "Hard", "Insane"];

export default function Challenges() {
  const { token } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [category, setCategory] = useState("All");
  const [difficulty, setDifficulty] = useState("All");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .challenges(token)
      .then(setChallenges)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const filtered = useMemo(() => {
    return challenges.filter(
      (c) =>
        (category === "All" || c.category === category) &&
        (difficulty === "All" || c.difficulty === difficulty)
    );
  }, [challenges, category, difficulty]);

  const solvedCount = challenges.filter((c) => c.solved).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>CTF Challenges</h1>
          <p className="subtitle">
            {challenges.length > 0
              ? `${solvedCount} / ${challenges.length} solved`
              : "Loading challenges..."}
          </p>
        </div>
        {challenges.length > 0 && (
          <div className="progress-ring-wrap">
            <div
              className="progress-ring"
              style={{
                "--pct": `${Math.round((solvedCount / challenges.length) * 100)}%`,
              }}
            >
              <span>{Math.round((solvedCount / challenges.length) * 100)}%</span>
            </div>
          </div>
        )}
      </div>

      <div className="filter-row">
        <div className="filter-bar">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={cat === category ? "filter-btn active" : "filter-btn"}
              onClick={() => setCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
        <div className="filter-bar">
          {DIFFICULTIES.map((d) => (
            <button
              key={d}
              className={
                d === difficulty ? `filter-btn diff-btn active diff-${d}` : `filter-btn diff-btn diff-${d}`
              }
              onClick={() => setDifficulty(d)}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      {!loading && filtered.length === 0 && (
        <p className="empty-state">No challenges match these filters.</p>
      )}

      <div className="challenge-grid">
        {filtered.map((c) => (
          <Link
            key={c.challenge_id}
            to={`/challenges/${c.challenge_id}`}
            className={`challenge-card ${c.solved ? "is-solved" : ""}`}
          >
            <div className="challenge-card-top">
              <span className="category-tag">{c.category}</span>
              <span className={`difficulty-badge diff-${c.difficulty}`}>{c.difficulty}</span>
            </div>
            <h3>{c.title}</h3>
            <p className="flag-format-hint">
              Flag format: <code>{c.flag_format}</code>
            </p>
            <div className="challenge-card-footer">
              <span className="points-pill">{c.points} pts</span>
              {c.solved && <span className="solved-tag">✓ Solved</span>}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
