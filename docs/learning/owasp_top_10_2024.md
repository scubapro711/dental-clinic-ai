# OWASP Top 10 2024 - Security Risks for DentalAI

**Date:** 2025-10-02  
**Epic:** L - Deep Learning Phase  
**User Story:** L.4 - Research Security Best Practices  
**Source:** https://www.reflectiz.com/blog/owasp-top-ten-2024/

---

## Overview

The OWASP (Open Worldwide Application Security Project) Top Ten ranks the most critical security risks to web applications. It is built from data gathered from an industry-wide survey and serves as an unofficial baseline for secure development. The next update is expected in early 2025.

---

## OWASP Top 10 Security Risks (2024)

### 1. Broken Access Control

**Description:**  
Access controls restrict users to only accessing resources and performing actions they are allowed to. Attackers can bypass these restrictions when developers leave certain doors open.

**Common Vulnerabilities:**
- Missing or inadequate authorization checks
- Insecure Direct Object References (IDOR) - users can manipulate URLs to access other users' data
- Privilege escalation - users can perform administrative actions they aren't entitled to

**Example Attack:**  
A user views their profile at `https://example.com/userprofiles/123`. An attacker changes the URL to `https://example.com/userprofiles/124` to access another user's profile without authorization.

**Mitigation Strategies:**
- Implement Role-Based Access Controls (RBAC) to clearly define roles and permissions
- Apply Principle of Least Privilege - give users minimum access privileges needed
- Use Indirect Object References (mappings or tokens) instead of direct database IDs in URLs
- Periodically review and test access controls
- Implement server-side authorization checks for every request

**DentalAI Implementation:**
- All API endpoints must verify user permissions before returning data
- Patient data access must be restricted by organization and role
- Admin functions must require admin role verification
- Use UUIDs instead of sequential IDs for resources
- Log all access control failures for monitoring

---

### 2. Cryptographic Failures

**Description:**  
Failures in cryptography that expose sensitive information like passwords, credit card numbers, or health records.

**Common Vulnerabilities:**
- Transmitting data over unencrypted networks (HTTP instead of HTTPS)
- Storing sensitive information in plain text
- Using outdated or insecure hashing algorithms (MD5, SHA-1)
- Improper key management (keys embedded in source code)
- Invalid or expired SSL/TLS certificates

**Mitigation Strategies:**
- Always use HTTPS with TLS 1.3 for data transmission
- Use strong encryption algorithms (AES-256) for data at rest and in transit
- Use robust hashing algorithms for passwords (bcrypt, scrypt, Argon2) with salting
- Store cryptographic keys in secure key management systems (AWS KMS, HashiCorp Vault)
- Regularly rotate encryption keys
- Validate SSL/TLS certificates promptly

**DentalAI Implementation:**
- All patient data encrypted at rest using AES-256
- All API communications over HTTPS/TLS 1.3
- Passwords hashed with bcrypt (cost factor 12)
- API keys and secrets stored in AWS Secrets Manager
- Database connection strings encrypted
- Regular SSL certificate renewal (Let's Encrypt with auto-renewal)

---

### 3. Injection

**Description:**  
Injection attacks occur when unauthorized user input is sent to an interpreter as part of a command or query, allowing attackers to execute malicious commands or access unauthorized data.

**Common Types:**
- SQL Injection - manipulating SQL queries
- Command Injection - executing OS commands
- LDAP Injection - manipulating LDAP statements
- XML Injection - manipulating XML parsers

**Example Attack:**  
A login form accepts username and password. An attacker enters `' OR '1'='1` as the username, which modifies the SQL query to always return true, bypassing authentication.

**Mitigation Strategies:**
- Sanitize all user inputs
- Use parameterized queries or prepared statements (never concatenate user input into queries)
- Perform input validation to ensure inputs conform to expectations
- Use ORM frameworks that automatically prevent injection
- Implement least privilege for database accounts

**DentalAI Implementation:**
- Use SQLAlchemy ORM with parameterized queries (no raw SQL with user input)
- Validate all user inputs against expected formats (email, phone, etc.)
- Use Pydantic models for input validation
- Escape special characters in user inputs
- Implement Content Security Policy (CSP) headers
- Use prepared statements for all database queries

---

### 4. Insecure Design

**Description:**  
Vulnerabilities introduced at the design stage rather than implementation stage, including missing security controls and poor architecture decisions.

**Common Issues:**
- Failing to validate or sanitize user inputs (by design)
- Insufficient authentication and authorization mechanisms
- Poor session management (inviting session hijacking)
- Poor error handling and logging (revealing system details)
- Insufficient data protection
- Overly complex or unnecessary features in core functionality
- Inadequate threat modeling
- Failure to build testing into lifecycle

**Mitigation Strategies:**
- Conduct threat modeling during design phase
- Follow secure design principles (defense in depth, fail securely, etc.)
- Implement security requirements from the start
- Use established security patterns and frameworks
- Conduct security reviews during design phase
- Build security testing into CI/CD pipeline

**DentalAI Implementation:**
- Threat model created for all major features before implementation
- Security requirements defined in Work Plan V14.0
- Multi-layered security (authentication, authorization, encryption, monitoring)
- Fail securely - errors don't reveal system details
- Minimal attack surface - only essential features in core functionality
- Security testing in every Epic's Definition of Done

---

### 5. Security Misconfiguration

**Description:**  
Vulnerabilities arising from poorly defined, implemented, or maintained security settings at any level of the application stack.

**Common Issues:**
- Using insecure default configurations (default passwords, default ports)
- Incomplete configurations (missing security controls)
- Sensitive debugging information left in production
- Unpatched systems (missing security updates)
- Directory listing enabled (exposing file structure)
- Unnecessary features or services enabled

**Mitigation Strategies:**
- Change all default credentials immediately
- Regularly apply security patches to all components
- Install only minimum required features
- Configure applications to handle errors securely without revealing details
- Use configuration management tools to enforce secure settings
- Conduct regular security audits
- Apply principle of least privilege
- Segment network to limit access and exposure

**DentalAI Implementation:**
- No default credentials (all passwords generated randomly)
- Automated security patching for OS and dependencies
- Minimal Docker images (only required packages)
- Production error messages don't reveal stack traces or system details
- Infrastructure as Code (Terraform) with security best practices
- Regular security audits (quarterly)
- Network segmentation (frontend, backend, database in separate subnets)
- Disable directory listing on web servers

---

### 6. Vulnerable and Outdated Components

**Description:**  
Using external dependencies (frameworks, libraries, plugins) that have known vulnerabilities or are no longer maintained.

**Common Issues:**
- Outdated components no longer maintained by vendor
- Unpatched libraries and frameworks
- Vulnerable plugins or extensions
- Using components with known CVEs (Common Vulnerabilities and Exposures)

**Mitigation Strategies:**
- Maintain inventory of all dependencies
- Regularly scan for vulnerabilities (Dependabot, Snyk, OWASP Dependency-Check)
- Keep all components up to date
- Remove unused dependencies
- Monitor security advisories for components in use
- Use Software Composition Analysis (SCA) tools

**DentalAI Implementation:**
- Dependabot enabled on GitHub for automatic dependency updates
- Weekly vulnerability scans with Snyk
- Automated dependency updates in CI/CD pipeline
- Remove unused dependencies during code reviews
- Pin dependency versions in requirements.txt and package.json
- Monitor security advisories for LangChain, FastAPI, React, PostgreSQL

---

### 7. Identification and Authentication Failures

**Description:**  
Failures in gatekeeping mechanisms that verify user identity and authenticate access.

**Common Issues:**
- Weak passwords ("password", "123456")
- Password reuse
- Brute-force attacks (trying all possible password combinations)
- Credential stuffing (using stolen username/password lists)
- Missing or weak Multi-Factor Authentication (MFA)
- Insecure session management
- Exposing session IDs in URLs

**Mitigation Strategies:**
- Enforce strong password policies (complexity, length, expiration)
- Implement Multi-Factor Authentication (MFA)
- Use account lockout mechanisms after failed login attempts
- Implement CAPTCHAs to prevent automated attacks
- Use secure session management (HttpOnly, Secure, SameSite cookies)
- Implement rate limiting on authentication endpoints
- Monitor for credential stuffing attacks

**DentalAI Implementation:**
- Password requirements: min 12 characters, uppercase, lowercase, numbers, symbols
- MFA required for all users (TOTP via authenticator app)
- Account lockout after 5 failed login attempts (15-minute cooldown)
- CAPTCHA on login after 3 failed attempts
- Secure session cookies (HttpOnly, Secure, SameSite=Strict)
- JWT tokens with short expiration (15 minutes) and refresh tokens
- Rate limiting on /auth endpoints (5 requests per minute per IP)
- Monitor for suspicious login patterns

---

### 8. Software and Data Integrity Failures

**Description:**  
Risks related to improper validation of software and data, where neither are adequately protected against unauthorized changes or corruption.

**Common Issues:**
- Insecure software updates (no signature verification)
- Lack of code signing
- Unsanitized data inputs
- Accepting serialized objects from untrusted sources
- CI/CD pipeline without integrity checks

**Mitigation Strategies:**
- Implement strong validation checks for software updates
- Use code signing to ensure authenticity
- Regularly audit and monitor integrity of software and data
- Use digital signatures for critical data
- Implement integrity checks in CI/CD pipeline
- Validate all data inputs before processing

**DentalAI Implementation:**
- Docker images signed and verified before deployment
- Git commits signed with GPG keys
- CI/CD pipeline validates checksums of dependencies
- Critical data (patient records) includes integrity hash
- Audit logs are write-only and tamper-evident
- Database backups include integrity verification
- No deserialization of untrusted data (use JSON only)

---

### 9. Security Logging and Monitoring Failures

**Description:**  
Inadequate logging and monitoring of security events, making it difficult to detect and respond to attacks.

**Common Issues:**
- Insufficient logging of security events
- Logs not centralized or protected
- No monitoring of logs for suspicious activities
- Logs don't include enough context (user, IP, timestamp)
- No alerting on security events
- Logs not retained long enough

**Mitigation Strategies:**
- Log all security-relevant events (authentication, authorization failures, input validation failures)
- Centralize logs in secure, tamper-proof storage
- Monitor logs for suspicious patterns
- Implement real-time alerting on critical events
- Retain logs for compliance requirements (7 years for healthcare)
- Protect logs from unauthorized access
- Include sufficient context in logs (user, IP, timestamp, action)

**DentalAI Implementation:**
- Comprehensive logging with structured JSON logs
- Centralized logging with AWS CloudWatch
- Log retention: 7 years (compliance with healthcare regulations)
- Real-time monitoring and alerting (Mission Control Dashboard)
- Log all authentication attempts, authorization failures, data access
- Logs include: user ID, organization ID, IP address, timestamp, action, result
- Tamper-proof logs (write-only, integrity-protected)
- Automated alerts for: failed logins, privilege escalation attempts, data exports

---

### 10. Server-Side Request Forgery (SSRF)

**Description:**  
Vulnerabilities that allow an attacker to make requests from the server to internal or external resources by manipulating user-controlled input.

**Common Issues:**
- Unrestricted URL access (server fetches any user-provided URL)
- Improper input validation on URLs
- Ability to access protected internal services
- No allowlist for external requests

**Example Attack:**  
An application allows users to provide a URL for profile picture upload. An attacker provides `http://localhost:6379` (Redis) or `http://169.254.169.254/latest/meta-data/` (AWS metadata service) to access internal services.

**Mitigation Strategies:**
- Strict input validation on all URLs
- Use allowlist of permitted domains/IPs
- Limit server's ability to access internal resources
- Network segmentation to protect sensitive services
- Disable unnecessary URL schemes (file://, gopher://, etc.)
- Use DNS resolution to validate URLs

**DentalAI Implementation:**
- No user-provided URLs accepted (except for specific whitelisted domains)
- If URL input needed, use strict allowlist (e.g., only allow image CDNs)
- Network segmentation prevents backend from accessing internal services
- Disable file:// and other dangerous URL schemes
- Validate and sanitize all URLs before making requests
- Use separate service account with minimal permissions for external requests

---

## Summary: Security Implementation for DentalAI

### Critical Security Controls:

1. **Authentication & Authorization:**
   - MFA for all users
   - RBAC with least privilege
   - Secure session management
   - Rate limiting on auth endpoints

2. **Data Protection:**
   - AES-256 encryption at rest
   - TLS 1.3 for data in transit
   - bcrypt for password hashing
   - Secrets in AWS Secrets Manager

3. **Input Validation:**
   - Pydantic models for all inputs
   - Parameterized queries (SQLAlchemy ORM)
   - No raw SQL with user input
   - CSP headers

4. **Dependency Management:**
   - Dependabot for automatic updates
   - Weekly vulnerability scans (Snyk)
   - Remove unused dependencies
   - Pin versions

5. **Logging & Monitoring:**
   - Comprehensive structured logging
   - Centralized logs (CloudWatch)
   - Real-time alerting
   - 7-year retention

6. **Secure Configuration:**
   - No default credentials
   - Automated security patching
   - Minimal Docker images
   - Network segmentation

7. **Secure Design:**
   - Threat modeling for all features
   - Security requirements from start
   - Multi-layered security
   - Security testing in CI/CD

8. **Integrity:**
   - Signed Docker images
   - Signed Git commits
   - Integrity checks in CI/CD
   - Tamper-proof audit logs

---

**Status:** OWASP Top 10 2024 learned ✅  
**Next:** Research healthcare-specific security (HIPAA, GDPR)
