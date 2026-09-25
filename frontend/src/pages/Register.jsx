import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import AuthHero from "../components/AuthHero.jsx";

export default function Register() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  // Password strength calculation
  const getPasswordStrength = (pass) => {
    if (!pass) return { score: 0, label: "Empty", color: "var(--border)" };
    let score = 0;
    if (pass.length >= 8) score++;
    if (pass.length >= 12) score++;
    if (/[A-Z]/.test(pass) && /[a-z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;

    if (score <= 2) return { score: 1, label: "Weak", color: "var(--danger)" };
    if (score <= 3) return { score: 2, label: "Medium", color: "var(--warn)" };
    return { score: 3, label: "Strong", color: "var(--accent)" };
  };

  const strength = getPasswordStrength(password);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = await api.register({ name, email, password });
      login(data.access_token, data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Failed to create account. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <AuthHero />

      <div className="auth-form-container">
        <form className="auth-card" onSubmit={handleSubmit}>
          <div className="auth-card-header">
            <div className="auth-icon-badge">🛡️</div>
            <h2>Create Clearance</h2>
            <p className="subtitle">Join AVST Lite and begin hands-on security training</p>
          </div>

          {error && (
            <div className="error-alert">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="reg-name">Full Name / Callsign</label>
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                id="reg-name"
                type="text"
                placeholder="Agent Smith"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                autoComplete="name"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="reg-email">Email Address</label>
            <div className="input-wrapper">
              <span className="input-icon">✉</span>
              <input
                id="reg-email"
                type="email"
                placeholder="analyst@agency.local"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="reg-pass">Password (min 8 chars)</label>
            <div className="input-wrapper">
              <span className="input-icon">🔒</span>
              <input
                id="reg-pass"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
                autoComplete="new-password"
              />
              <button
                type="button"
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "👁️‍🗨️"}
              </button>
            </div>
            {password.length > 0 && (
              <div className="password-strength-wrap">
                <div className="strength-bars">
                  <span className={`str-bar ${strength.score >= 1 ? "active" : ""}`} style={{ backgroundColor: strength.score >= 1 ? strength.color : undefined }} />
                  <span className={`str-bar ${strength.score >= 2 ? "active" : ""}`} style={{ backgroundColor: strength.score >= 2 ? strength.color : undefined }} />
                  <span className={`str-bar ${strength.score >= 3 ? "active" : ""}`} style={{ backgroundColor: strength.score >= 3 ? strength.color : undefined }} />
                </div>
                <span className="strength-label" style={{ color: strength.color }}>{strength.label}</span>
              </div>
            )}
          </div>

          <button type="submit" className="auth-submit-btn" disabled={busy}>
            {busy ? (
              <span className="btn-loading">
                <span className="spinner-icon"></span> Creating Profile...
              </span>
            ) : (
              <span>Register Account ➔</span>
            )}
          </button>

          <div className="auth-card-footer">
            <p className="switch">
              Already possess clearance? <Link to="/login">Sign in</Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
