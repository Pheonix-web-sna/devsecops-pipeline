# ==============================================================================
# LABORATORY DEMONSTRATION DOCKERFILE - DO NOT DEPLOY IN PRODUCTION
# This file intentionally contains container misconfigurations for Trivy/Checkov detection.
# ==============================================================================

# VULNERABILITY 1: Using an older base image with known vulnerabilities (Target: Trivy CVE scan)
# REMEDIATION: Use a hardened, minimal, and actively updated base image (e.g., python:3.11-slim-bookworm)
FROM python:3.9-slim

# VULNERABILITY 2: Hardcoded fictional secret in build environment (Target: Trivy, Gitleaks, Secret Scanners)
# REMEDIATION: Never bake secrets into images; pass runtime secrets via Kubernetes Secrets or Docker Compose env_file.
ENV DEMO_BUILD_TOKEN="fictional-lab-docker-token-xyz987"

# Set working directory
WORKDIR /app

# VULNERABILITY 3: Running apt-get without cleaning cache or verifying packages (Target: Checkov CKV_DOCKER_3)
# REMEDIATION: Combine update and install, and rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y curl

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# VULNERABILITY 4: Missing USER directive; container runs as root by default (Target: Checkov CKV_DOCKER_8, Trivy)
# REMEDIATION: Create a non-root group and user, e.g.:
# RUN groupadd -r appuser && useradd -r -g appuser appuser
# USER appuser

# Expose internal port
EXPOSE 5000

# Healthcheck missing (Target: Checkov CKV_DOCKER_2)
# REMEDIATION: Add HEALTHCHECK --interval=30s --timeout=3s CMD curl -f http://127.0.0.1:5000/health || exit 1

CMD ["python", "app.py"]
