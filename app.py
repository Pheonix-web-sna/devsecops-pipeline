import sqlite3
from flask import Flask, request, render_template, render_template_string, jsonify
from markupsafe import Markup

# ==============================================================================
# DEVSECOPS SECURITY PIPELINE DEMONSTRATION APPLICATION
# LABORATORY USE ONLY - LOCALHOST ONLY (127.0.0.1)
# ==============================================================================

app = Flask(__name__)

# --- DEMONSTRATION VULNERABILITY 1: HARDCODED SECRETS (SAST / SECRET SCAN) ---
# Scanner Target: Gitleaks, Bandit (B105/B106)
# Risk: Secrets committed to source control lead to unauthorized infrastructure access.
# Secure Remediation: Load secrets via environment variables or secret vaults (e.g., AWS Secrets Manager, HashiCorp Vault).
DEMO_SECRET_API_KEY = "ak-live-labtest-998877665544332211"  # pragma: allowlist secret
DEMO_FICTIONAL_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"              # Fictional lab key for Gitleaks
DEMO_FICTIONAL_DB_PASSWORD = "LabAdminSecretPassword123!"     # Fictional hardcoded credential


def get_db_connection():
    """Initializes an in-memory SQLite database populated with non-sensitive dummy data."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            email TEXT
        )
    """)
    cursor.executemany("""
        INSERT INTO users (username, role, email) VALUES (?, ?, ?)
    """, [
        ("alice", "developer", "alice@example.local"),
        ("bob", "devsecops", "bob@example.local"),
        ("charlie", "auditor", "charlie@example.local")
    ])
    conn.commit()
    return conn


@app.route("/")
def index():
    """Landing dashboard describing the DevSecOps lab endpoints."""
    return render_template("index.html")


# --- DEMONSTRATION VULNERABILITY 2: SQL INJECTION (SQLi) ---
# Scanner Target: Bandit (B608), GitHub CodeQL
# Risk: Raw string concatenation allows attackers to bypass authentication or extract data.
@app.route("/api/vulnerable/users")
def vulnerable_sql():
    """
    VULNERABLE ENDPOINT: Demonstrates SQL Injection via unvalidated string formatting.
    Example payload: /api/vulnerable/users?role=' OR '1'='1
    """
    role = request.args.get("role", "developer")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Insecure: direct concatenation into SQL string
    query = f"SELECT id, username, role, email FROM users WHERE role = '{role}'"
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        results = [{"id": r[0], "username": r[1], "role": r[2], "email": r[3]} for r in rows]
        return jsonify({"status": "vulnerable_query_executed", "executed_query": query, "data": results})
    except Exception as e:
        return jsonify({"error": str(e), "executed_query": query}), 400
    finally:
        conn.close()


@app.route("/api/secure/users")
def secure_sql():
    """
    SECURE REMEDIATION: Uses parameterized queries (prepared statements).
    """
    role = request.args.get("role", "developer")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Secure: parameter substitution
    query = "SELECT id, username, role, email FROM users WHERE role = ?"
    cursor.execute(query, (role,))
    rows = cursor.fetchall()
    results = [{"id": r[0], "username": r[1], "role": r[2], "email": r[3]} for r in rows]
    conn.close()
    return jsonify({"status": "secure_parameterized_query", "data": results})


# --- DEMONSTRATION VULNERABILITY 3: REFLECTED CROSS-SITE SCRIPTING (XSS) ---
# Scanner Target: Bandit (B701 / Jinja autoescape), CodeQL
# Risk: Reflecting unsanitized user input allows client-side script execution.
@app.route("/vulnerable/greet")
def vulnerable_xss():
    """
    VULNERABLE ENDPOINT: Reflects unescaped user input directly into HTML.
    Example payload: /vulnerable/greet?name=<script>alert('XSS')</script>
    """
    name = request.args.get("name", "Student")
    # Insecure: unescaped rendering using Markup or raw HTML interpolation
    html_response = f"""
    <div style="font-family: sans-serif; padding: 20px;">
        <h3>Demonstration: Reflected XSS</h3>
        <p>Hello, {name}!</p>
        <p><a href="/">Back to Dashboard</a></p>
    </div>
    """
    return Markup(html_response)


@app.route("/secure/greet")
def secure_xss():
    """
    SECURE REMEDIATION: Relies on Jinja2 auto-escaping or explicit escaping.
    """
    name = request.args.get("name", "Student")
    # Secure: render template string with automatic HTML escaping
    return render_template_string("""
    <div style="font-family: sans-serif; padding: 20px;">
        <h3>Demonstration: Secured Greet</h3>
        <p>Hello, {{ name }}!</p>
        <p><a href="/">Back to Dashboard</a></p>
    </div>
    """, name=name)


@app.route("/health")
def health():
    """Basic health check endpoint for testing and monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "devsecops-demo-pipeline",
        "environment": "laboratory-localhost"
    }), 200


if __name__ == "__main__":
    # STRICT SAFETY LIMITATION:
    # 1. Bind strictly to localhost (127.0.0.1)
    # 2. Never bind to 0.0.0.0
    # 3. Debug mode disabled for safety
    app.run(host="127.0.0.1", port=5000, debug=False)
