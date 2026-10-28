# DevSecOps CI/CD Security Pipeline

[![Security Pipeline](https://github.com/your-username/devsecops-pipeline/actions/workflows/security.yml/badge.svg)](https://github.com)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.11%20%7C%203.13-blue)](https://www.python.org/)
[![Security Scanners](https://img.shields.io/badge/scanners-Bandit%20%7C%20pip--audit%20%7C%20Gitleaks%20%7C%20Checkov%20%7C%20Trivy%20%7C%20CodeQL-green)](#security-pipeline-scanners)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> **ACADEMIC & LABORATORY DEMONSTRATION ONLY**  
> This project contains deliberately vulnerable code, outdated dependencies, and misconfigured infrastructure files to demonstrate static analysis, dependency scanning, secret detection, and IaC policy verification.  
> **Bind exclusively to `127.0.0.1`. Never deploy this demonstration code to production or public-facing servers.**

---

## 1. Project Objective & DevSecOps Overview

The core philosophy of **DevSecOps** is to "shift security left"—integrating automated security controls directly into the software development lifecycle (SDLC) rather than treating security as an afterthought.

### Core Objectives:
1. **Automate Vulnerability Discovery**: Detect application code vulnerabilities, dependency CVEs, committed secrets, and cloud configuration errors automatically on every `push` and `pull_request`.
2. **Prevent Drift and Secret Exposure**: Identify high-entropy API keys and tokens before code enters protected production branches.
3. **Bridge Development and Security**: Deliver actionable SARIF reports directly to developers inside GitHub's Security dashboard.

---

## 2. Architecture & Folder Structure

```
DevSecOps CI/CD Security Pipeline/
├── .github/
│   ├── codeql/
│   │   └── codeql-config.yml       # GitHub CodeQL static analysis rules
│   └── workflows/
│       └── security.yml            # Unified GitHub Actions security pipeline
├── terraform/
│   └── main.tf                     # Laboratory IaC misconfigurations (for Checkov)
├── templates/
│   └── index.html                  # Localhost dashboard explaining lab endpoints
├── tests/
│   └── test_app.py                 # Pytest test suite for functional validation
├── .dockerignore                   # Build exclusion rules
├── .gitignore                      # Git exclusion rules (caches, venvs, reports)
├── Dockerfile                      # Laboratory container misconfigurations (for Trivy)
├── app.py                          # Flask app with SQLi, XSS, & secret demonstrations
├── requirements.txt                # Outdated pinned packages for SCA scanning
└── README.md                       # Comprehensive guide and documentation
```

---

## 3. Local Setup & Execution (Localhost Only)

### Prerequisites:
- Python 3.9+ (Python 3.11 or 3.13 tested)
- Git

### Step-by-Step Setup:
```bash
# 1. Clone your repository (or navigate to workspace)
cd "Cybersecurity Training Workspace"

# 2. Create and activate a Python virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
# source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask application (restricted strictly to 127.0.0.1)
python app.py
```
Open your browser to: **`http://127.0.0.1:5000`**

### Demonstration Endpoints:
- `http://127.0.0.1:5000/` : Interactive Dashboard
- `http://127.0.0.1:5000/api/vulnerable/users?role=' OR '1'='1` : SQL Injection demonstration
- `http://127.0.0.1:5000/api/secure/users?role=developer` : Secure parameterized SQL query
- `http://127.0.0.1:5000/vulnerable/greet?name=<script>alert('XSS')</script>` : Reflected XSS demonstration
- `http://127.0.0.1:5000/secure/greet?name=Student` : Secure auto-escaped template
- `http://127.0.0.1:5000/health` : System health check endpoint

---

## 4. Local Testing & Security Scan Commands

You can execute the same checks locally before pushing code:

### Run Functional Tests:
```bash
pytest -v tests/
```

### Run Python SAST (Bandit):
```bash
pip install bandit
bandit -r app.py
```

### Run Dependency SCA (pip-audit):
```bash
pip install pip-audit
pip-audit -r requirements.txt
```

### Run Secret Scanner (Gitleaks):
```bash
# Using Gitleaks standalone binary:
gitleaks detect --source . --verbose
```

### Run Infrastructure as Code Scanner (Checkov):
```bash
pip install checkov
checkov -d terraform/
```

### Run Container Misconfiguration Scanner (Trivy):
```bash
trivy config Dockerfile
```

---

## 5. Security Scanner Matrix & Expected Findings

| Scanner | Category | Target | Expected Finding | Severity |
| :--- | :--- | :--- | :--- | :--- |
| **Bandit** | Python SAST | `app.py` | `B105/B106`: Hardcoded password/key string<br>`B608`: SQL string formatting | HIGH / MEDIUM |
| **pip-audit** | SCA | `requirements.txt` | CVEs in `requests 2.25.1` and `Werkzeug 2.0.1` | HIGH / MODERATE |
| **Gitleaks** | Secret Detection | Git History & Files | Fictional AWS access key token match | HIGH |
| **Checkov** | IaC Security | `terraform/main.tf` | `CKV_AWS_20`: S3 bucket public-read ACL<br>`CKV_AWS_24`: Unrestricted SSH port 22 ingress<br>`CKV_AWS_3`: Unencrypted EBS volume | HIGH / MEDIUM |
| **Trivy** | Filesystem & Docker | `Dockerfile` | Running as root user (`CKV_DOCKER_8`), outdated base image vulnerabilities | HIGH / MEDIUM |
| **CodeQL** | Deep Code SAST | Entire Repo | Taint tracking showing user input flow into SQL/DOM queries | HIGH |

---

## 6. Pipeline Modes: Demo vs. Strict Mode

The GitHub Actions workflow (`.github/workflows/security.yml`) provides two operational modes:

### DEMO MODE (Default for Academic Evaluation):
- **Behavior**: Scanners run, generate detailed console logs, export SARIF reports, and upload artifacts. The job does not abruptly fail on findings because `continue-on-error: true` is configured.
- **Purpose**: Enables the instructor or evaluator to see all tools run successfully in a single pipeline execution without earlier scanner findings blocking later jobs.

### STRICT MODE (Production Quality Gate):
To convert the pipeline into an enforcing security gate:
1. Open `.github/workflows/security.yml`.
2. Locate the scanner steps (`bandit`, `pip_audit`, `gitleaks`, `checkov`, `trivy`).
3. Set `continue-on-error: false`.
4. Configure exit thresholds:
   ```yaml
   - name: Run Bandit (Strict)
     run: bandit -r app.py --severity-level high -c bandit.yaml
   ```
5. Any high-severity vulnerability or unapproved secret will immediately reject the pull request or fail the build.

---

## 7. Vulnerability Remediation Guide

### 1. SQL Injection (`app.py`):
- **Vulnerable Code**:
  ```python
  cursor.execute(f"SELECT * FROM users WHERE role = '{role}'")
  ```
- **Remediation**:
  ```python
  cursor.execute("SELECT * FROM users WHERE role = ?", (role,))
  ```

### 2. Reflected Cross-Site Scripting (`app.py`):
- **Vulnerable Code**:
  ```python
  return Markup(f"<h1>Hello, {name}</h1>")
  ```
- **Remediation**:
  ```python
  return render_template_string("<h1>Hello, {{ name }}</h1>", name=name)
  ```

### 3. Hardcoded Secrets (`app.py` & `Dockerfile`):
- **Vulnerable Code**:
  ```python
  AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
  ```
- **Remediation**:
  ```python
  import os
  AWS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
  ```

### 4. Vulnerable Dependencies (`requirements.txt`):
- **Vulnerable Code**:
  ```
  Flask==2.0.1
  Werkzeug==2.0.1
  requests==2.25.1
  ```
- **Remediation**:
  ```
  Flask>=3.0.0
  Werkzeug>=3.0.1
  requests>=2.31.0
  ```

### 5. Insecure Terraform Infrastructure (`terraform/main.tf`):
- **Vulnerable Code**:
  ```hcl
  acl = "public-read"
  cidr_blocks = ["0.0.0.0/0"] # SSH Port 22
  encrypted = false
  ```
- **Remediation**:
  ```hcl
  # S3: Private bucket with public access block
  # SG: Restrict to trusted CIDR, e.g., ["10.0.0.0/16"]
  # EBS: encrypted = true, kms_key_id = aws_kms_key.app_key.arn
  ```

---

## 8. GitHub Security Features, Actions Logs & Alerts

### Viewing Pipeline Artifacts and Logs:
1. Navigate to the **Actions** tab in your GitHub repository.
2. Click on the latest workflow run: **"DevSecOps CI/CD Security Pipeline"**.
3. View logs under each step: **Run Bandit**, **Run pip-audit**, **Run Checkov**, etc.
4. Scroll to the bottom to download the zip artifact: **`devsecops-security-reports`**.

### GitHub Advanced Security (GHAS) & CodeQL:
- In **PUBLIC** repositories on GitHub, GitHub Advanced Security (CodeQL, Dependabot alerts, Secret Scanning alerts) is **100% FREE**.
- To view CodeQL findings: Navigate to the **Security** tab &rarr; **Code scanning alerts**.
- To view Dependabot alerts: Navigate to the **Security** tab &rarr; **Dependabot alerts**.

### Free Alternatives When GHAS is Restricted (e.g. Private Free Repos):
If your repository is private and GHAS is unavailable:
1. **Bandit & pip-audit CLI Outputs**: The pipeline dumps human-readable reports directly in the GitHub Actions step logs.
2. **Downloadable Artifacts**: The workflow packages all generated SARIF, JSON, and TXT reports into a downloadable GitHub Actions artifact.
3. **Third-Party Free Tiers**: Use free community tools like Snyk (free 200 tests/month) or Trivy OSS.

---

## 9. Pushing to Your Own PUBLIC GitHub Repository

Follow these exact steps to push this project to GitHub for academic submission:

### Step 1: Create a Public Repository on GitHub
1. Sign in to [github.com](https://github.com).
2. Click the **`+`** icon in the upper right corner &rarr; **New repository**.
3. Name your repository (e.g., `devsecops-cicd-pipeline`).
4. Set repository visibility to **Public** (Important: Enables free CodeQL and Security tab alerts).
5. **Do NOT** check "Add a README file", ".gitignore", or "Choose a license" (we already created them).
6. Click **Create repository**.

### Step 2: Initialize Git and Push Local Code
Open PowerShell or Terminal in this project folder and run:

```bash
# 1. Initialize local Git repository
git init

# 2. Stage all files
git add .

# 3. Create initial commit
git commit -m "feat: complete DevSecOps security pipeline project"

# 4. Set branch to main
git branch -M main

# 5. Link to your GitHub repository (replace with your actual GitHub URL)
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git

# 6. Push code to GitHub
git push -u origin main
```

---

## 10. Repository Security Settings Checklist

Before submitting your assignment, verify these repository settings:
1. [ ] Go to **Settings** &rarr; **Code security and analysis**.
2. [ ] Ensure **Dependabot alerts** is set to `Enabled`.
3. [ ] Ensure **Dependabot security updates** is set to `Enabled`.
4. [ ] Ensure **Secret scanning** and **Push protection** are toggled `On`.
5. [ ] Go to **Actions** &rarr; confirm the workflow finishes and shows green/completed.
6. [ ] Go to **Security** &rarr; verify alert entries for Bandit, CodeQL, and Dependabot.

---

## 11. Optional Industry Integrations (Overview)

For enterprise DevSecOps maturity, organizations integrate specialized platforms (no accounts or paid subscriptions required for this assignment):
- **Snyk**: Comprehensive SCA, container, and IaC vulnerability engine with direct PR auto-fix pull requests.
- **Wiz**: Cloud-Native Application Protection Platform (CNAPP) mapping cloud runtime telemetry back to source code.
- **Checkmarx (CxOne / KICS)**: Enterprise-grade SAST and open-source infrastructure scanning engine.
- **Orca Security**: Agentless cloud infrastructure scanning analyzing storage snapshots for vulnerabilities, secrets, and misconfigurations.

---

## License & Compliance
This project is released under the MIT License for educational and research purposes.
