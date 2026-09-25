import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import AuthHero from "../components/AuthHero.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const data = await api.login({ email, password });
      login(data.access_token, data.user);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
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
            <div className="auth-icon-badge">⚡</div>
            <h2>Welcome Back</h2>
            <p className="subtitle">Sign in to your AVST Lite security operations center</p>
          </div>

          {error && (
            <div className="error-alert">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="login-email">Email Address</label>
            <div className="input-wrapper">
              <span className="input-icon">✉</span>
              <input
                id="login-email"
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
            <label htmlFor="login-pass">Password</label>
            <div className="input-wrapper">
              <span className="input-icon">🔒</span>
              <input
                id="login-pass"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
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
          </div>

          <button type="submit" className="auth-submit-btn" disabled={busy}>
            {busy ? (
              <span className="btn-loading">
                <span className="spinner-icon"></span> Authenticating...
              </span>
            ) : (
              <span>Sign In ➔</span>
            )}
          </button>

          <div className="auth-card-footer">
            <p className="switch">
              Don't have an account? <Link to="/register">Register here</Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
