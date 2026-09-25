import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

export default function ChallengeDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const [challenge, setChallenge] = useState(null);
  const [flag, setFlag] = useState("");
  const [submitResult, setSubmitResult] = useState(null);
  const [question, setQuestion] = useState("");
  const [hintLevel, setHintLevel] = useState(1);
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    api.challenge(token, id).then(setChallenge).catch(() => {});
  }, [token, id]);

  async function handleSubmitFlag(e) {
    e.preventDefault();
    const result = await api.submitFlag(token, id, flag);
    setSubmitResult(result);
    if (result.correct) {
      setChallenge((c) => ({ ...c, solved: true }));
    }
  }

  async function handleDownload(filename) {
    setDownloading(true);
    try {
      await api.downloadFile(token, id, filename);
    } catch (err) {
      setSubmitResult({ correct: false, message: `Download failed: ${err.message}` });
    } finally {
      setDownloading(false);
    }
  }

  async function handleAskHint(e) {
    e.preventDefault();
    if (!question.trim()) return;
    setAsking(true);
    const userMsg = { role: "student", text: question };
    setMessages((m) => [...m, userMsg]);
    try {
      const res = await api.getHint(token, id, question, hintLevel);
      setMessages((m) => [
        ...m,
        { role: "ai", text: res.hint, source: res.source, level: res.hint_level },
      ]);
      setHintLevel((lvl) => Math.min(lvl + 1, 3));
    } catch (err) {
      setMessages((m) => [...m, { role: "ai", text: `Error: ${err.message}` }]);
    } finally {
      setQuestion("");
      setAsking(false);
    }
  }

  if (!challenge) return <div className="page">Loading...</div>;

  return (
    <div className="page challenge-detail">
      <div className="challenge-main">
        <div className="challenge-tags">
          <span className="category-tag">{challenge.category}</span>
          <span className={`difficulty-badge diff-${challenge.difficulty}`}>
            {challenge.difficulty}
          </span>
        </div>
        <h1>{challenge.title}</h1>
        <p className="points">{challenge.points} points</p>
        <p className="description">
          {challenge.description.split(/(https?:\/\/[^\s)]+)/g).map((part, i) =>
            part.match(/^https?:\/\//) ? (
              <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="challenge-link">
                {part}
              </a>
            ) : (
              part
            )
          )}
        </p>
        {challenge.download_file && (
          <button
            type="button"
            className="download-btn"
            onClick={() => handleDownload(challenge.download_file)}
            disabled={downloading}
          >
            {downloading ? "Downloading..." : `⬇ Download ${challenge.download_file}`}
          </button>
        )}
        {challenge.docker_lab && (
          <div className="lab-info">
            <div className="lab-info-header">
              <span>🚀 Practical lab available: <code>{challenge.docker_lab}</code></span>
              {challenge.docker_lab === "sqli-lab" && (
                <a
                  href="http://localhost:5001/lab/sqli-login"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="lab-link-btn"
                >
                  Open Lab (Port 5001) ↗
                </a>
              )}
              {challenge.docker_lab === "xss-lab" && (
                <a
                  href="http://localhost:5002/lab/xss-search"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="lab-link-btn"
                >
                  Open Lab (Port 5002) ↗
                </a>
              )}
            </div>
            <p className="lab-setup-note">
              Setup: run <code>docker compose up --build</code> in <code>docker/</code> directory.
            </p>
          </div>
        )}

        <div className="flag-format-box">
          Flag format: <code>{challenge.flag_format}</code>
        </div>

        <form className="flag-form" onSubmit={handleSubmitFlag}>
          <input
            placeholder={challenge.flag_format}
            value={flag}
            onChange={(e) => setFlag(e.target.value)}
            disabled={challenge.solved}
          />
          <button type="submit" disabled={challenge.solved}>
            {challenge.solved ? "Solved" : "Submit Flag"}
          </button>
        </form>
        {submitResult && (
          <div className={submitResult.correct ? "result success" : "result failure"}>
            {submitResult.message}
            {submitResult.points_awarded > 0 && ` (+${submitResult.points_awarded} pts)`}
          </div>
        )}
      </div>

      <div className="hint-panel">
        <h2>AI Hint Assistant</h2>
        <p className="hint-subtitle">Ask a question — the AI gives progressive hints, never the answer.</p>
        <div className="chat-window">
          {messages.length === 0 && (
            <p className="chat-empty">Ask something like "Why didn't my payload work?"</p>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`}>
              {m.role === "ai" && m.source && (
                <span className="chat-source">{m.source === "ollama" ? "AI" : "Guide"}</span>
              )}
              {m.text}
            </div>
          ))}
        </div>
        <form className="chat-input" onSubmit={handleAskHint}>
          <input
            placeholder="Ask the AI assistant..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={asking}
          />
          <button type="submit" disabled={asking}>
            {asking ? "..." : "Ask"}
          </button>
        </form>
      </div>
    </div>
  );
}
