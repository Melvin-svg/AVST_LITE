import React, { useEffect, useState } from "react";

const TYPING_LINES = [
  { type: "input", text: '$ curl /lab/sqli-login -d "user=admin\' --"' },
  { type: "output", text: "200 OK — welcome admin!", className: "dim" },
  { type: "input", text: "$ submit_flag AVST{...}" },
  { type: "output", text: "✓ Flag accepted! +100 points", className: "ok" },
  { type: "input", text: "$ nmap -sV 10.10.10.42" },
  { type: "output", text: "22/tcp  open  ssh   OpenSSH 8.9", className: "dim" },
  { type: "output", text: "80/tcp  open  http  Apache 2.4.54", className: "dim" },
];

export default function AuthHero() {
  const [visibleLines, setVisibleLines] = useState(0);

  useEffect(() => {
    if (visibleLines < TYPING_LINES.length) {
      const delay = TYPING_LINES[visibleLines]?.type === "input" ? 1200 : 600;
      const timer = setTimeout(() => setVisibleLines((v) => v + 1), delay);
      return () => clearTimeout(timer);
    } else {
      // Loop after pause
      const timer = setTimeout(() => setVisibleLines(0), 3000);
      return () => clearTimeout(timer);
    }
  }, [visibleLines]);

  return (
    <div className="auth-hero">
      <div className="auth-hero-badge">
        <span className="badge-dot"></span>
        AVST LITE — Cybersecurity Training Platform
      </div>
      <h1>
        Learn cybersecurity
        <br />
        <span className="hero-gradient-text">by breaking things safely.</span>
      </h1>
      <p>
        Capture-the-flag challenges across web security, cryptography, forensics and
        reverse engineering — with an AI assistant that nudges, never spoils.
      </p>

      <div className="auth-features">
        <div className="auth-feature">
          <span className="auth-feature-icon">🏴</span>
          <span>CTF Challenges</span>
        </div>
        <div className="auth-feature">
          <span className="auth-feature-icon">🤖</span>
          <span>AI Hints</span>
        </div>
        <div className="auth-feature">
          <span className="auth-feature-icon">🛡️</span>
          <span>Live CVE Feed</span>
        </div>
      </div>

      <div className="terminal-mock">
        <div className="terminal-bar">
          <span className="dot red" />
          <span className="dot yellow" />
          <span className="dot green" />
          <span className="terminal-title">avst-lite — zsh</span>
        </div>
        <div className="terminal-body">
          {TYPING_LINES.slice(0, visibleLines).map((line, i) => (
            <div
              key={i}
              className={`terminal-line ${line.className || ""}`}
              style={{ animationDelay: `${i * 0.08}s` }}
            >
              {line.type === "input" && <span className="prompt">$</span>}
              <span className={line.type === "input" ? "typing-text" : ""}>
                {line.text.replace("$ ", "")}
              </span>
            </div>
          ))}
          {visibleLines < TYPING_LINES.length && (
            <span className="cursor-blink">▊</span>
          )}
        </div>
      </div>
    </div>
  );
}
