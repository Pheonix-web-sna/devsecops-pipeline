# ==============================================================================
# LABORATORY DEMONSTRATION TERRAFORM - DO NOT DEPLOY TO PRODUCTION
# This configuration contains intentional Infrastructure as Code (IaC) misconfigurations
# designed for detection by scanners like Checkov and Trivy.
# Fictional parameters and identifiers only.
# ==============================================================================

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  # Mock/sandbox configuration - never execute terraform apply with real credentials
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

# --- MISCONFIGURATION 1: S3 BUCKET PUBLIC READ & UNENCRYPTED ---
# Scanner Target: Checkov (CKV_AWS_20, CKV_AWS_19, CKV_AWS_21), Trivy
# Risk: Data leakage and public exposure of sensitive organizational data.
# Secure Remediation: Enable server-side encryption (AES256/KMS), block public access, enable versioning.
resource "aws_s3_bucket" "insecure_demo_bucket" {
  bucket = "lab-demo-fictional-security-bucket-xyz123"

  # MISCONFIGURATION: Deprecated public ACL
  # Remediation: acl = "private" and attach aws_s3_bucket_public_access_block
  # checkov:skip=CKV2_AWS_61:Lab demo purpose
}

resource "aws_s3_bucket_acl" "insecure_acl" {
  bucket = aws_s3_bucket.insecure_demo_bucket.id
  acl    = "public-read" # Deliberate misconfiguration
}

# --- MISCONFIGURATION 2: SECURITY GROUP WITH UNRESTRICTED INGRESS ---
# Scanner Target: Checkov (CKV_AWS_24, CKV_AWS_260)
# Risk: Port 22 (SSH) open to 0.0.0.0/0 exposes servers to automated brute force attacks.
# Secure Remediation: Restrict CIDR blocks to specific trusted corporate bastion/VPN IPs.
resource "aws_security_group" "insecure_web_sg" {
  name        = "lab-insecure-sg"
  description = "Demonstration insecure security group"

  # Insecure SSH Rule
  ingress {
    description = "Unrestricted SSH ingress - Deliberate Lab Vulnerability"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # VULNERABLE: Open to the entire world
  }

  # Insecure Plaintext HTTP
  ingress {
    description = "Plaintext HTTP open to world"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- MISCONFIGURATION 3: UNENCRYPTED EBS VOLUME ---
# Scanner Target: Checkov (CKV_AWS_3)
# Risk: Unencrypted persistent storage risks physical and snapshot data disclosure.
# Secure Remediation: Set encrypted = true and specify kms_key_id.
resource "aws_ebs_volume" "insecure_volume" {
  availability_zone = "us-east-1a"
  size              = 10
  encrypted         = false # VULNERABLE: Storage is not encrypted at rest

  tags = {
    Environment = "Security-Demo-Lab"
  }
}
