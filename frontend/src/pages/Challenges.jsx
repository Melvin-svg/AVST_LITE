import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const CATEGORIES = ["All", "Web Security", "Cryptography", "Forensics", "Reverse Engineering"];

export default function Challenges() {
  const { token } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [filter, setFilter] = useState("All");

  useEffect(() => {
    api.challenges(token).then(setChallenges).catch(() => {});
  }, [token]);

  const filtered =
    filter === "All" ? challenges : challenges.filter((c) => c.category === filter);

  return (
    <div className="page">
      <h1>CTF Challenges</h1>
      <div className="filter-bar">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            className={cat === filter ? "filter-btn active" : "filter-btn"}
            onClick={() => setFilter(cat)}
          >
            {cat}
          </button>
        ))}
      </div>
      <div className="challenge-grid">
        {filtered.map((c) => (
          <Link key={c.challenge_id} to={`/challenges/${c.challenge_id}`} className="challenge-card">
            <div className="challenge-card-top">
              <span className="category-tag">{c.category}</span>
              {c.solved && <span className="solved-tag">Solved</span>}
            </div>
            <h3>{c.title}</h3>
            <p>{c.points} points</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
