import React from "react";

export default function AuthHero() {
  return (
    <div className="auth-hero">
      <div className="auth-hero-badge">AVST LITE</div>
      <h1>Learn cybersecurity by breaking things safely.</h1>
      <p>
        Capture-the-flag challenges across web security, cryptography, forensics and
        reverse engineering — with an AI assistant that nudges, never spoils.
      </p>
      <div className="terminal-mock">
        <div className="terminal-bar">
          <span className="dot red" />
          <span className="dot yellow" />
          <span className="dot green" />
        </div>
        <div className="terminal-body">
          <div>
            <span className="prompt">$</span> curl /lab/sqli-login -d "user=admin' --"
          </div>
          <div className="dim">200 OK — welcome admin!</div>
          <div>
            <span className="prompt">$</span> submit_flag AVST{"{"}...{"}"}
          </div>
          <div className="ok">+100 points</div>
        </div>
      </div>
    </div>
  );
}
