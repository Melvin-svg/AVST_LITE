from flask import Flask, request, render_template_string

app = Flask(__name__)

PAGE = """
<h2>Site Search</h2>
<form method="get">
  <input name="q" value="{{ q }}">
  <button type="submit">Search</button>
</form>
<p>Results for: {{ q|safe }}</p>
<script>
  if (window.__avst_xss_triggered) {
    document.title = "AVST{reflected_xss_alert_1}";
  }
</script>
"""


@app.route("/lab/xss-search")
def search():
    # Intentionally vulnerable: reflects user input without escaping (for teaching purposes only)
    q = request.args.get("q", "")
    return render_template_string(PAGE, q=q)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)
