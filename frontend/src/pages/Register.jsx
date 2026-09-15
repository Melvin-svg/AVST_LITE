import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext.jsx";
import AuthHero from "../components/AuthHero.jsx";

export default function Register() {
  const [name, setName] = useState("");
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
      const data = await api.register({ name, email, password });
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
        <h2>Create your account</h2>
        <p className="subtitle">Join AVST Lite and start learning.</p>
        {error && <div className="error">{error}</div>}
        <label>Name</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required />
        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          minLength={8}
          required
        />
        <button type="submit" disabled={busy}>
          {busy ? "Creating account..." : "Register"}
        </button>
        <p className="switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </form>
    </div>
  );
}
