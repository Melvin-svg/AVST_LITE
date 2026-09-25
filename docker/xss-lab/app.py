from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Site Search — AVST Lite Lab</title>
  <style>
    :root {
      --bg: #090d16;
      --panel: #131d33;
      --border: #223257;
      --accent: #3fd68a;
      --blue: #5b9dff;
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
      max-width: 520px;
      padding: 24px;
    }
    .badge {
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--blue);
      background: rgba(91, 157, 255, 0.12);
      border: 1px solid rgba(91, 157, 255, 0.3);
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
    .search-form {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
    }
    input {
      flex: 1;
      background: #0e1526;
      border: 1px solid var(--border);
      color: #fff;
      padding: 10px 14px;
      border-radius: 8px;
      font-size: 0.95rem;
      outline: none;
    }
    input:focus {
      border-color: var(--blue);
    }
    button {
      background: linear-gradient(135deg, #2b74dd, var(--blue));
      border: none;
      color: #fff;
      padding: 10px 18px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
    }
    button:hover { opacity: 0.95; }
    .results-box {
      background: #0e1526;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 14px 16px;
      font-size: 0.9rem;
      min-height: 48px;
      margin-bottom: 16px;
      word-break: break-all;
    }
    .flag-banner {
      display: none;
      background: rgba(63, 214, 138, 0.15);
      border: 1px solid var(--accent);
      color: var(--accent);
      padding: 14px 16px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.95rem;
      margin-bottom: 16px;
      animation: fadeIn 0.3s ease-out;
    }
    .hints-box {
      font-size: 0.78rem;
      color: var(--muted);
      border-top: 1px solid var(--border);
      padding-top: 14px;
      line-height: 1.5;
    }
    code {
      font-family: monospace;
      color: var(--blue);
      background: rgba(91, 157, 255, 0.1);
      padding: 2px 4px;
      border-radius: 4px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <span class="badge">AVST LITE LAB 5002 • REFLECTED XSS</span>
      <h2>Site Query Search</h2>
      <p class="subtitle">Search public database. Injected scripts are evaluated directly in context.</p>

      <form class="search-form" method="get" action="/lab/xss-search">
        <input name="q" value="{{ q }}" placeholder="e.g. security advisory" autofocus>
        <button type="submit">Search</button>
      </form>

      <div class="results-box">
        <strong>Query Output:</strong> {{ q|safe }}
      </div>

      <div id="flag-banner" class="flag-banner">
        🎉 <strong>XSS Exploit Successful!</strong><br>
        Captured Flag: <code>AVST{reflected_xss_alert_1}</code>
      </div>

      <div class="hints-box">
        <strong>Directives:</strong> The page script inspects <code>window.__avst_xss_triggered</code>. Inject JavaScript to assign this flag variable to true. The flag is also exposed in the browser tab title.
      </div>
    </div>
  </div>

  <script>
    if (window.__avst_xss_triggered) {
      document.title = "AVST{reflected_xss_alert_1}";
      var banner = document.getElementById("flag-banner");
      if (banner) banner.style.display = "block";
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return redirect("/lab/xss-search")


@app.route("/lab/xss-search")
def search():
    # Intentionally vulnerable: reflects user input without escaping (for teaching purposes only)
    q = request.args.get("q", "")
    return render_template_string(PAGE, q=q)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
