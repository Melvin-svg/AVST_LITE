import sqlite3
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
DB = "lab.db"

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Staff Portal — AVST Lite Lab</title>
  <style>
    :root {
      --bg: #090d16;
      --panel: #131d33;
      --border: #223257;
      --accent: #3fd68a;
      --danger: #ff5c72;
      --text: #edf2fc;
      --muted: #8293b5;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .container {
      width: 100%;
      max-width: 440px;
      padding: 24px;
    }
    .badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--accent);
      background: rgba(63, 214, 138, 0.12);
      border: 1px solid rgba(63, 214, 138, 0.3);
      padding: 4px 10px;
      border-radius: 20px;
      margin-bottom: 12px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 32px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    h2 {
      margin: 0 0 8px;
      font-size: 1.5rem;
    }
    .subtitle {
      color: var(--muted);
      font-size: 0.88rem;
      margin: 0 0 24px;
    }
    .form-group {
      margin-bottom: 16px;
    }
    label {
      display: block;
      font-size: 0.82rem;
      font-weight: 600;
      color: var(--muted);
      margin-bottom: 6px;
    }
    input {
      width: 100%;
      background: #0e1526;
      border: 1px solid var(--border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
    }
    input:focus {
      border-color: var(--accent);
    }
    button {
      width: 100%;
      background: linear-gradient(135deg, #22b06a, var(--accent));
      border: none;
      color: #06170d;
      padding: 12px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
      margin-top: 10px;
    }
    button:hover { opacity: 0.95; }
    .message {
      margin-top: 18px;
      padding: 12px 14px;
      border-radius: 8px;
      font-size: 0.88rem;
      line-height: 1.4;
      background: rgba(255, 92, 114, 0.12);
      border: 1px solid var(--danger);
      color: var(--danger);
      word-break: break-all;
    }
    .message.success {
      background: rgba(63, 214, 138, 0.15);
      border-color: var(--accent);
      color: var(--accent);
      font-weight: 700;
    }
    .hints-box {
      margin-top: 20px;
      font-size: 0.78rem;
      color: var(--muted);
      border-top: 1px solid var(--border);
      padding-top: 14px;
    }
    code {
      font-family: monospace;
      color: var(--accent);
      background: rgba(63, 214, 138, 0.1);
      padding: 2px 4px;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <span class="badge">AVST LITE LAB 5001 • SQL INJECTION</span>
      <h2>Staff Authentication</h2>
      <p class="subtitle">Internal administration gateway. Bypass query validation to gain access.</p>
      
      <form method="post" action="/lab/sqli-login">
        <div class="form-group">
          <label>Username</label>
          <input name="username" placeholder="e.g. admin" required autofocus>
        </div>
        <div class="form-group">
          <label>Password</label>
          <input name="password" type="password" placeholder="••••••••">
        </div>
        <button type="submit">Sign In</button>
      </form>

      {% if message %}
      <div class="message {% if 'AVST{' in message %}success{% endif %}">
        {{ message }}
      </div>
      {% endif %}

      <div class="hints-box">
        <strong>Directives:</strong> The backend query directly concatenates inputs: <code>SELECT * FROM users WHERE username='&lt;user&gt;' AND password='&lt;pass&gt;'</code>. Try breaking out with a single quote.
      </div>
    </div>
  </div>
</body>
</html>
"""


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)")
    conn.execute("DELETE FROM users")
    conn.execute("INSERT INTO users VALUES ('admin', 'S3cretPass!', 'admin')")
    conn.execute("INSERT INTO users VALUES ('guest', 'guest123', 'user')")
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return redirect("/lab/sqli-login")


@app.route("/lab/sqli-login", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Intentionally vulnerable: raw string concatenation (for teaching purposes only)
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        conn = sqlite3.connect(DB)
        try:
            cur = conn.execute(query)
            row = cur.fetchone()
        except sqlite3.Error as e:
            row = None
            message = f"DB Error: {e}"
        conn.close()

        if row:
            if row[2] == "admin":
                message = "Welcome admin! AVST{sql_injection_login_bypass}"
            else:
                message = f"Welcome {row[0]}!"
        elif not message:
            message = "Invalid credentials."

    return render_template_string(PAGE, message=message)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=False)
