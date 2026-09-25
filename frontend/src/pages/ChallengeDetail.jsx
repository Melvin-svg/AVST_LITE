import React, { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";

const QUICK_HINTS = [
  "What security tools should I utilize?",
  "What is the theoretical concept behind this?",
  "Give me a subtle nudge in the right direction.",
  "What kind of payload structure is expected?",
];

export default function ChallengeDetail() {
  const { id } = useParams();
  const { token } = useAuth();
  const [challenge, setChallenge] = useState(null);
  const [flag, setFlag] = useState("");
  const [submitResult, setSubmitResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [question, setQuestion] = useState("");
  const [hintLevel, setHintLevel] = useState(1);
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [copiedFormat, setCopiedFormat] = useState(false);
  const [copiedDockerCmd, setCopiedDockerCmd] = useState(false);
  const [labStatus, setLabStatus] = useState("checking"); // 'online', 'offline', 'checking'

  const chatEndRef = useRef(null);

  useEffect(() => {
    api.challenge(token, id).then(setChallenge).catch(() => {});
  }, [token, id]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  const checkLabStatus = () => {
    if (!challenge?.docker_lab) return;
    const port = challenge.docker_lab === "sqli-lab" ? 5001 : challenge.docker_lab === "xss-lab" ? 5002 : null;
    if (!port) return;

    setLabStatus("checking");
    const checkUrl = `http://localhost:${port}/`;
    fetch(checkUrl, { mode: "no-cors" })
      .then(() => setLabStatus("online"))
      .catch(() => setLabStatus("offline"));
  };

  useEffect(() => {
    if (challenge?.docker_lab) {
      checkLabStatus();
    }
  }, [challenge]);

  async function handleSubmitFlag(e) {
    e.preventDefault();
    if (!flag.trim()) return;
    setSubmitting(true);
    setSubmitResult(null);
    try {
      const result = await api.submitFlag(token, id, flag.trim());
      setSubmitResult(result);
      if (result.correct) {
        setChallenge((c) => ({ ...c, solved: true }));
      }
    } catch (err) {
      setSubmitResult({ correct: false, message: `Submission error: ${err.message}` });
    } finally {
      setSubmitting(false);
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

  async function sendHintQuestion(qText) {
    if (!qText.trim() || asking) return;
    setAsking(true);
    const userMsg = { role: "student", text: qText };
    setMessages((m) => [...m, userMsg]);
    try {
      const res = await api.getHint(token, id, qText, hintLevel);
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

  const handleCopyFormat = () => {
    if (challenge?.flag_format) {
      navigator.clipboard.writeText(challenge.flag_format);
      setCopiedFormat(true);
      setTimeout(() => setCopiedFormat(false), 2000);
    }
  };

  const handleCopyDockerCmd = () => {
    navigator.clipboard.writeText("cd docker && docker compose up -d");
    setCopiedDockerCmd(true);
    setTimeout(() => setCopiedDockerCmd(false), 2000);
  };

  if (!challenge) {
    return (
      <div className="page challenge-detail-loading">
        <div className="loading-spinner"></div>
        <p>Decoupling challenge payload & directives...</p>
      </div>
    );
  }

  const labUrl =
    challenge.docker_lab === "sqli-lab"
      ? "http://localhost:5001/lab/sqli-login"
      : challenge.docker_lab === "xss-lab"
      ? "http://localhost:5002/lab/xss-search"
      : null;

  return (
    <div className="page challenge-detail-page">
      {/* Breadcrumb Navigation */}
      <div className="challenge-breadcrumb">
        <Link to="/challenges">← Back to Challenges</Link>
        <span className="crumb-sep">/</span>
        <span className="crumb-cat">{challenge.category}</span>
        <span className="crumb-sep">/</span>
        <span className="crumb-current">{challenge.title}</span>
      </div>

      <div className="challenge-detail-grid">
        {/* Main Dossier Column */}
        <div className="challenge-main-panel cyber-panel">
          <div className="dossier-header">
            <div className="dossier-tags">
              <span className="category-tag">{challenge.category}</span>
              <span className={`difficulty-badge diff-${challenge.difficulty}`}>
                {challenge.difficulty}
              </span>
              <span className="points-pill">+{challenge.points} pts</span>
            </div>
            {challenge.solved && (
              <span className="solved-status-badge">
                <span className="check-icon">✓</span> Target Solved
              </span>
            )}
          </div>

          <h1 className="challenge-title">{challenge.title}</h1>

          {/* Mission Briefing Box */}
          <div className="mission-briefing-box">
            <div className="box-title-bar">
              <span className="term-dot"></span>
              <span>MISSION DOSSIER & DIRECTIVES</span>
            </div>
            <div className="briefing-content">
              {challenge.description.split(/(https?:\/\/[^\s)]+)/g).map((part, i) =>
                part.match(/^https?:\/\//) ? (
                  <a
                    key={i}
                    href={part}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="challenge-link"
                  >
                    {part} ↗
                  </a>
                ) : (
                  part
                )
              )}
            </div>
          </div>

          {/* Download Artifact */}
          {challenge.download_file && (
            <div className="artifact-download-card">
              <div className="artifact-info">
                <span className="artifact-icon">📦</span>
                <div>
                  <strong>Challenge Artifact:</strong>
                  <span className="artifact-name">{challenge.download_file}</span>
                </div>
              </div>
              <button
                type="button"
                className="download-btn"
                onClick={() => handleDownload(challenge.download_file)}
                disabled={downloading}
              >
                {downloading ? "Decrypting File..." : `⬇ Download Artifact`}
              </button>
            </div>
          )}

          {/* Docker Containerized Lab Info */}
          {challenge.docker_lab && (
            <div className="lab-info-card">
              <div className="lab-info-header">
                <div className="lab-title">
                  <span className={`lab-badge-pulse ${labStatus === "online" ? "online" : labStatus === "offline" ? "offline" : ""}`}></span>
                  <strong>
                    Live Target Environment: <code>{challenge.docker_lab}</code>
                  </strong>
                  {labStatus === "online" && (
                    <span className="lab-status-online-pill">🟢 Online & Active</span>
                  )}
                  {labStatus === "offline" && (
                    <span className="lab-status-offline-pill">🔴 Container Offline</span>
                  )}
                </div>

                <div className="lab-actions">
                  <button
                    type="button"
                    className="lab-check-btn"
                    onClick={checkLabStatus}
                    title="Refresh connection status"
                  >
                    🔄
                  </button>

                  {labUrl && (
                    <a
                      href={labUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="lab-launch-btn"
                    >
                      Open Target ({challenge.docker_lab === "sqli-lab" ? "Port 5001" : "Port 5002"}) ↗
                    </a>
                  )}
                </div>
              </div>

              {labStatus === "offline" && (
                <div className="lab-offline-alert">
                  <span>⚠️ Target container is not reachable. Launch it with:</span>
                  <div className="cmd-copy-wrap">
                    <code>cd docker && docker compose up -d</code>
                    <button type="button" onClick={handleCopyDockerCmd} className="copy-cmd-btn">
                      {copiedDockerCmd ? "Copied! ✓" : "Copy Command"}
                    </button>
                  </div>
                </div>
              )}

              {labStatus === "online" && (
                <div className="lab-online-tip">
                  ✓ Container is running. Click <strong>Open Target ↗</strong> to view the interactive vulnerable application in a new tab.
                </div>
              )}
            </div>
          )}

          {/* Conceptual / Analytical Challenge Directive Info */}
          {!challenge.docker_lab && !challenge.download_file && (
            <div className="analytical-challenge-card">
              <div className="analytical-card-header">
                <span className="analytical-icon">🧠</span>
                <div>
                  <strong>Analytical & Conceptual Scenario</strong>
                  <p>
                    This mission does not require an external host. Study the payload or tokens
                    in the dossier above, or engage the Tactical AI Advisor on the right to deduce the flag.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Flag Submission Terminal Box */}
          <div className="flag-submission-section">
            <div className="flag-format-header">
              <span>Accepted Flag Format:</span>
              <code onClick={handleCopyFormat} title="Click to copy">
                {challenge.flag_format}
              </code>
              <button
                type="button"
                className="copy-format-btn"
                onClick={handleCopyFormat}
              >
                {copiedFormat ? "Copied! ✓" : "Copy Format"}
              </button>
            </div>

            <form className="flag-form" onSubmit={handleSubmitFlag}>
              <div className="flag-input-wrap">
                <span className="flag-icon">🚩</span>
                <input
                  type="text"
                  placeholder={challenge.flag_format || "AVST{...}"}
                  value={flag}
                  onChange={(e) => setFlag(e.target.value)}
                  disabled={challenge.solved || submitting}
                  className="flag-input"
                />
              </div>
              <button
                type="submit"
                className={`flag-submit-btn ${challenge.solved ? "solved" : ""}`}
                disabled={challenge.solved || submitting}
              >
                {challenge.solved
                  ? "Objective Solved ✓"
                  : submitting
                  ? "Verifying..."
                  : "Submit Flag ➔"}
              </button>
            </form>

            {submitResult && (
              <div
                className={`submission-result-banner ${
                  submitResult.correct ? "success-banner" : "failure-banner"
                }`}
              >
                <span className="result-icon">
                  {submitResult.correct ? "🎉" : "❌"}
                </span>
                <div className="result-text">
                  <strong>{submitResult.message}</strong>
                  {submitResult.points_awarded > 0 && (
                    <span className="awarded-pill">
                      +{submitResult.points_awarded} Points Added!
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* AI Hint Operations Center */}
        <div className="hint-panel cyber-panel">
          <div className="hint-panel-header">
            <div className="hint-avatar-icon">🤖</div>
            <div>
              <h2>Tactical AI Advisor</h2>
              <p className="hint-subtitle">
                Level {hintLevel} Clearance — Progressive nudges without spoiling answers.
              </p>
            </div>
          </div>

          {/* Quick suggestions */}
          <div className="quick-prompts-container">
            <span className="quick-prompt-label">Quick Directives:</span>
            <div className="quick-prompt-chips">
              {QUICK_HINTS.map((hint, i) => (
                <button
                  key={i}
                  type="button"
                  className="quick-chip"
                  onClick={() => sendHintQuestion(hint)}
                  disabled={asking}
                >
                  {hint}
                </button>
              ))}
            </div>
          </div>

          {/* Chat transcript */}
          <div className="chat-window">
            {messages.length === 0 && (
              <div className="chat-welcome-state">
                <span className="chat-icon-huge">📡</span>
                <p>
                  Encountering resistance? Ask the AI advisor for conceptual
                  clarification, payload suggestions, or diagnostic advice.
                </p>
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`chat-bubble ${m.role}`}>
                {m.role === "ai" && (
                  <div className="chat-source-tag">
                    <span className="source-dot"></span>
                    <span>
                      {m.source === "ollama" ? "OLLAMA LLM ADVISOR" : "TACTICAL ADVISOR"}
                      {m.level ? ` • LEVEL ${m.level}` : ""}
                    </span>
                  </div>
                )}
                <div className="chat-bubble-content">{m.text}</div>
              </div>
            ))}

            {asking && (
              <div className="chat-bubble ai typing">
                <div className="chat-source-tag">
                  <span className="source-dot pulse"></span>
                  <span>ANALYZING QUERY...</span>
                </div>
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Chat input */}
          <form
            className="chat-input-row"
            onSubmit={(e) => {
              e.preventDefault();
              sendHintQuestion(question);
            }}
          >
            <input
              type="text"
              placeholder="Ask for guidance (e.g., 'What is causing my SQL query to fail?')..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={asking}
            />
            <button type="submit" disabled={asking || !question.trim()}>
              {asking ? "..." : "Send"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
