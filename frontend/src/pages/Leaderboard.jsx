import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function Leaderboard() {
  const { token, user } = useAuth();
  const [rows, setRows] = useState([]);

  useEffect(() => {
    api.leaderboard(token).then(setRows).catch(() => {});
  }, [token]);

  return (
    <div className="page">
      <h1>Leaderboard</h1>
      <table className="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Solved</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={r.user_id} className={r.user_id === user?.user_id ? "me" : ""}>
              <td>
                {i < 3 ? <span className={`medal medal-${i}`}>#{i + 1}</span> : `#${i + 1}`}
              </td>
              <td>{r.name}</td>
              <td>{r.solved_count}</td>
              <td>{r.total_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
