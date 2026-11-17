"""
test_server/vulnerable_app.py

A tiny, deliberately vulnerable local Flask app, provided ONLY as a safe
practice target for modules/sql_tester.py. It builds a SQL query by
string concatenation on purpose so you have something legitimate to test
the SQLi tester against, instead of pointing it at a site you don't own.

Run with:  python test_server/vulnerable_app.py
Then in the toolkit's SQL Injection Tester, target:
  http://127.0.0.1:5050/user?id=1

DO NOT deploy this app anywhere public. It exists only for localhost
practice.
"""

import sqlite3

from flask import Flask, request

app = Flask(__name__)
DB_PATH = "/tmp/vulnerable_practice.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS users")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, email TEXT)")
    conn.executemany(
        "INSERT INTO users (id, username, email) VALUES (?, ?, ?)",
        [
            (1, "alice", "alice@example.local"),
            (2, "bob", "bob@example.local"),
            (3, "carol", "carol@example.local"),
        ],
    )
    conn.commit()
    conn.close()


@app.route("/user")
def get_user():
    user_id = request.args.get("id", "1")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Intentionally vulnerable: string concatenation instead of a
    # parameterized query. This is the exact mistake the SQL tester
    # is designed to detect.
    query = f"SELECT id, username, email FROM users WHERE id = {user_id}"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        return {"query": query, "results": rows}
    except sqlite3.Error as e:
        conn.close()
        return {"query": query, "error": str(e)}, 500


@app.route("/")
def index():
    return (
        "Vulnerable practice server is running.<br>"
        "Try: <a href='/user?id=1'>/user?id=1</a><br>"
        "This exists only for local SQLi-tester practice."
    )


if __name__ == "__main__":
    init_db()
    print("Vulnerable practice server: http://127.0.0.1:5050  (localhost only)")
    app.run(host="127.0.0.1", port=5050, debug=False)
