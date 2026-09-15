import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import AuthHero from "../components/AuthHero.jsx";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page">
      <AuthHero />

      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Welcome back</h2>
        <p className="subtitle">Sign in to continue your training.</p>
        {error && <div className="error">{error}</div>}
        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={busy}>
          {busy ? "Signing in..." : "Login"}
        </button>
        <p className="switch">
          No account? <Link to="/register">Register</Link>
        </p>
      </form>
    </div>
  );
}
