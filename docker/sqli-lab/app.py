import sqlite3

from flask import Flask, request, render_template_string

app = Flask(__name__)
DB = "lab.db"

PAGE = """
<h2>Staff Login</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
"""


def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, role TEXT)")
    conn.execute("DELETE FROM users")
    conn.execute("INSERT INTO users VALUES ('admin', 'S3cretPass!', 'admin')")
    conn.execute("INSERT INTO users VALUES ('guest', 'guest123', 'user')")
    conn.commit()
    conn.close()


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
            message = f"DB error: {e}"
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
