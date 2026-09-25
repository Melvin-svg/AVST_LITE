import React, { useEffect, useState, useMemo } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function Leaderboard() {
  const { token, user } = useAuth();
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .leaderboard(token)
      .then(setRows)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const filteredRows = useMemo(() => {
    if (!search.trim()) return rows;
    return rows.filter((r) =>
      r.name?.toLowerCase().includes(search.toLowerCase().trim())
    );
  }, [rows, search]);

  const top3 = rows.slice(0, 3);
  const myRank = rows.findIndex((r) => r.user_id === user?.user_id) + 1;

  return (
    <div className="page leaderboard-page">
      <div className="page-header">
        <div>
          <div className="header-eyebrow">GLOBAL OPERATOR STANDINGS</div>
          <h1>Hall of Fame & Leaderboard</h1>
          <p className="subtitle">
            Rankings and points standings updated across all active training cohorts.
          </p>
        </div>

        {myRank > 0 && (
          <div className="my-rank-banner">
            <span className="my-rank-label">Your Current Standing:</span>
            <span className="my-rank-val">Rank #{myRank}</span>
          </div>
        )}
      </div>

      {/* Top 3 Podium Showcase */}
      {top3.length > 0 && (
        <div className="podium-container">
          {/* 2nd Place */}
          {top3[1] && (
            <div className="podium-card rank-2">
              <div className="podium-medal">🥈</div>
              <div className="podium-avatar">
                {top3[1].name?.[0]?.toUpperCase() || "2"}
              </div>
              <span className="podium-name">{top3[1].name}</span>
              <span className="podium-score">{top3[1].total_score} pts</span>
              <span className="podium-solves">{top3[1].solved_count} Solves</span>
              <div className="podium-pedestal p2">
                <span>#2</span>
              </div>
            </div>
          )}

          {/* 1st Place */}
          {top3[0] && (
            <div className="podium-card rank-1">
              <div className="podium-crown">👑</div>
              <div className="podium-medal">🥇</div>
              <div className="podium-avatar champ">
                {top3[0].name?.[0]?.toUpperCase() || "1"}
              </div>
              <span className="podium-name">{top3[0].name}</span>
              <span className="podium-score">{top3[0].total_score} pts</span>
              <span className="podium-solves">{top3[0].solved_count} Solves</span>
              <div className="podium-pedestal p1">
                <span>#1 APEX</span>
              </div>
            </div>
          )}

          {/* 3rd Place */}
          {top3[2] && (
            <div className="podium-card rank-3">
              <div className="podium-medal">🥉</div>
              <div className="podium-avatar">
                {top3[2].name?.[0]?.toUpperCase() || "3"}
              </div>
              <span className="podium-name">{top3[2].name}</span>
              <span className="podium-score">{top3[2].total_score} pts</span>
              <span className="podium-solves">{top3[2].solved_count} Solves</span>
              <div className="podium-pedestal p3">
                <span>#3</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Table Search Controls */}
      <div className="leaderboard-table-controls">
        <div className="table-search-wrap">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by operative callsign or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {search && (
            <button className="clear-search-btn" onClick={() => setSearch("")}>
              ✕
            </button>
          )}
        </div>
        <span className="operative-count-tag">
          {filteredRows.length} Operative{filteredRows.length === 1 ? "" : "s"} Listed
        </span>
      </div>

      {/* Full Leaderboard Table */}
      <div className="table-container">
        <table className="leaderboard-table">
          <thead>
            <tr>
              <th className="th-rank">Rank</th>
              <th>Operative</th>
              <th className="th-center">Objectives Cleared</th>
              <th className="th-right">Accumulated Score</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan="4" className="table-loading-cell">
                  Loading operator standings...
                </td>
              </tr>
            )}

            {!loading && filteredRows.length === 0 && (
              <tr>
                <td colSpan="4" className="table-empty-cell">
                  No operatives match your search query.
                </td>
              </tr>
            )}

            {filteredRows.map((r, i) => {
              const isMe = r.user_id === user?.user_id;
              const globalIndex = rows.indexOf(r);
              return (
                <tr key={r.user_id} className={`table-row ${isMe ? "me" : ""}`}>
                  <td className="td-rank">
                    {globalIndex === 0 ? (
                      <span className="medal-badge gold">🥇 #1</span>
                    ) : globalIndex === 1 ? (
                      <span className="medal-badge silver">🥈 #2</span>
                    ) : globalIndex === 2 ? (
                      <span className="medal-badge bronze">🥉 #3</span>
                    ) : (
                      <span className="rank-num">#{globalIndex + 1}</span>
                    )}
                  </td>
                  <td className="td-name">
                    <div className="user-profile-cell">
                      <span className="table-avatar">
                        {r.name?.[0]?.toUpperCase() || "?"}
                      </span>
                      <div className="user-titles">
                        <span className="user-realname">{r.name}</span>
                        {isMe && <span className="you-pill">YOU</span>}
                      </div>
                    </div>
                  </td>
                  <td className="th-center">
                    <span className="solved-badge">{r.solved_count} Solved</span>
                  </td>
                  <td className="th-right">
                    <span className="score-badge">{r.total_score} pts</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
