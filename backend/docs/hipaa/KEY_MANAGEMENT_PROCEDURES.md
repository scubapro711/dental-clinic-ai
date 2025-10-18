# DentaFlow - Key Management & Encryption Procedures

**Version:** 1.0  
**Date:** October 18, 2025  
**Owner:** Eran Sarfaty, Security Officer

---

## 1. Overview

This document defines the key management and encryption procedures for DentaFlow to ensure the confidentiality and integrity of Protected Health Information (PHI) in compliance with HIPAA Security Rule (45 CFR § 164.312).

**Objectives:**
- Protect PHI at rest and in transit using industry-standard encryption
- Implement secure key generation, storage, rotation, and destruction
- Maintain audit trails for all key management operations
- Comply with HIPAA encryption requirements

---

## 2. Encryption Standards

### 2.1 Data at Rest

**Database (Cloud SQL):**
- **Algorithm:** AES-256
- **Implementation:** Google-managed encryption keys (automatic)
- **Scope:** All database files, backups, and replicas

**File Storage (Cloud Storage):**
- **Algorithm:** AES-256
- **Implementation:** Google-managed encryption keys (automatic)
- **Scope:** All objects in GCS buckets

**Application-Level PHI Encryption:**
- **Algorithm:** AES-128-CBC
- **Implementation:** Custom encryption service (app/services/encryption_service.py)
- **Scope:** Sensitive PHI fields (SSN, medical notes, etc.)
- **Key Management:** Environment variables (current), GCP Secret Manager (planned)

### 2.2 Data in Transit

**HTTPS/TLS:**
- **Protocol:** TLS 1.2 or higher
- **Cipher Suites:** Strong ciphers only (AES-GCM, ChaCha20-Poly1305)
- **Certificate:** Let's Encrypt (auto-renewed)
- **Scope:** All API endpoints, frontend, admin dashboard

**Database Connections:**
- **Protocol:** SSL/TLS
- **Implementation:** Cloud SQL Proxy with SSL enforcement
- **Scope:** All backend-to-database connections

**External APIs:**
- **Odoo:** HTTPS with API key authentication
- **Stripe:** HTTPS with API key authentication
- **LLM APIs:** HTTPS with API key authentication

---

## 3. Key Types and Hierarchy

### 3.1 Key Hierarchy

```
Root Keys (GCP KMS)
    ↓
Data Encryption Keys (DEK)
    ↓
Application Encryption Keys
    ↓
Encrypted PHI
```

### 3.2 Key Types

| Key Type | Purpose | Algorithm | Rotation | Storage |
|----------|---------|-----------|----------|---------|
| **Root Key (KEK)** | Encrypt DEKs | AES-256 | Automatic (GCP KMS) | GCP KMS |
| **Data Encryption Key (DEK)** | Encrypt PHI | AES-128 | 90 days | Encrypted in DB |
| **JWT Secret** | Sign auth tokens | HS256 | 180 days | GCP Secret Manager |
| **Session Secret** | Encrypt sessions | AES-256 | 90 days | GCP Secret Manager |
| **Stripe API Key** | Payment processing | N/A | Manual | GCP Secret Manager |
| **Odoo API Key** | ERP integration | N/A | Manual | GCP Secret Manager |
| **LLM API Keys** | AI services | N/A | Manual | GCP Secret Manager |

---

## 4. Current Implementation

### 4.1 Environment Variables (Current State)

**Location:** `.env` file, Cloud Run environment variables

**Keys Currently in Environment:**
```bash
# Encryption
ENCRYPTION_KEY=<32-byte-hex>  # AES-128 key for PHI

# JWT
JWT_SECRET_KEY=<random-string>  # HS256 signing key

# Database
DATABASE_PASSWORD=<password>  # Cloud SQL password

# External APIs
ODOO_API_KEY=<key>
STRIPE_SECRET_KEY=<key>
OPENAI_API_KEY=<key>
ANTHROPIC_API_KEY=<key>
```

**Issues with Current Approach:**
- ❌ Keys visible in environment (low security)
- ❌ No automatic rotation
- ❌ No audit trail
- ❌ Difficult to manage across environments
- ❌ Risk of accidental exposure (logs, errors)

---

## 5. Planned Migration to GCP Secret Manager

### 5.1 Architecture

```
Application (Cloud Run)
    ↓ (IAM authentication)
GCP Secret Manager
    ↓ (encrypted at rest with GCP KMS)
Secrets (keys, passwords, API tokens)
```

### 5.2 Migration Plan

**Phase 1: Setup (Week 2, Day 1-2)**

```bash
# 1. Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com --project=dentaflow-prod

# 2. Create service account for Cloud Run
gcloud iam service-accounts create dentaflow-backend-sa \
  --display-name="DentaFlow Backend Service Account" \
  --project=dentaflow-prod

# 3. Grant Secret Manager access
gcloud projects add-iam-policy-binding dentaflow-prod \
  --member="serviceAccount:dentaflow-backend-sa@dentaflow-prod.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# 4. Create secrets
echo -n "$ENCRYPTION_KEY" | gcloud secrets create encryption-key \
  --data-file=- \
  --replication-policy="automatic" \
  --project=dentaflow-prod

echo -n "$JWT_SECRET_KEY" | gcloud secrets create jwt-secret \
  --data-file=- \
  --replication-policy="automatic" \
  --project=dentaflow-prod

# Repeat for all secrets...
```

**Phase 2: Update Application Code (Week 2, Day 3)**

```python
# app/core/secrets.py (NEW)

from google.cloud import secretmanager
import os
from functools import lru_cache

class SecretManager:
    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "dentaflow-prod")
        self.client = secretmanager.SecretManagerServiceClient()
    
    @lru_cache(maxsize=128)
    def get_secret(self, secret_id: str, version: str = "latest") -> str:
        """
        Retrieve secret from GCP Secret Manager.
        Results are cached for performance.
        """
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
        response = self.client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    
    def get_encryption_key(self) -> bytes:
        """Get PHI encryption key."""
        key_hex = self.get_secret("encryption-key")
        return bytes.fromhex(key_hex)
    
    def get_jwt_secret(self) -> str:
        """Get JWT signing secret."""
        return self.get_secret("jwt-secret")
    
    def get_database_password(self) -> str:
        """Get database password."""
        return self.get_secret("database-password")
    
    def get_api_key(self, service: str) -> str:
        """Get external API key."""
        return self.get_secret(f"{service}-api-key")

# Singleton instance
secret_manager = SecretManager()
```

**Phase 3: Update Encryption Service (Week 2, Day 3)**

```python
# app/services/encryption_service.py (UPDATED)

from app.core.secrets import secret_manager
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

class EncryptionService:
    def __init__(self):
        # Get key from Secret Manager instead of environment
        self.key = secret_manager.get_encryption_key()
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt PHI data."""
        iv = os.urandom(16)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad plaintext to block size
        padded = self._pad(plaintext.encode('utf-8'))
        ciphertext = encryptor.update(padded) + encryptor.finalize()
        
        # Return base64(iv + ciphertext)
        return base64.b64encode(iv + ciphertext).decode('utf-8')
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt PHI data."""
        data = base64.b64decode(ciphertext)
        iv = data[:16]
        encrypted = data[16:]
        
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        padded = decryptor.update(encrypted) + decryptor.finalize()
        plaintext = self._unpad(padded)
        
        return plaintext.decode('utf-8')
```

**Phase 4: Update Cloud Run Deployment (Week 2, Day 4)**

```bash
# Deploy with Secret Manager integration
gcloud run deploy dentaflow-backend \
  --image=gcr.io/dentaflow-prod/backend:latest \
  --service-account=dentaflow-backend-sa@dentaflow-prod.iam.gserviceaccount.com \
  --set-secrets=ENCRYPTION_KEY=encryption-key:latest,JWT_SECRET=jwt-secret:latest \
  --region=us-central1 \
  --project=dentaflow-prod
```

**Phase 5: Remove Environment Variables (Week 2, Day 5)**

```bash
# Remove secrets from .env and Cloud Run environment
# Keep only non-sensitive config (DB_HOST, etc.)
```

---

## 6. Key Rotation Procedures

### 6.1 Automatic Rotation (GCP KMS)

**Root Keys (KEK):**
- **Frequency:** Automatic (GCP manages)
- **Process:** Transparent, no downtime
- **Audit:** GCP Cloud Audit Logs

### 6.2 Manual Rotation (Application Keys)

**Data Encryption Keys (DEK):**

**Frequency:** Every 90 days

**Process:**
```bash
# 1. Generate new key
NEW_KEY=$(openssl rand -hex 16)

# 2. Add new version to Secret Manager
echo -n "$NEW_KEY" | gcloud secrets versions add encryption-key \
  --data-file=- \
  --project=dentaflow-prod

# 3. Re-encrypt all PHI with new key (migration script)
python3 scripts/rotate-encryption-key.py \
  --old-version=1 \
  --new-version=2

# 4. Verify re-encryption
python3 scripts/verify-encryption.py --version=2

# 5. Disable old key version (after 30 days)
gcloud secrets versions disable 1 --secret=encryption-key --project=dentaflow-prod

# 6. Destroy old key version (after 90 days)
gcloud secrets versions destroy 1 --secret=encryption-key --project=dentaflow-prod
```

**JWT Secret:**

**Frequency:** Every 180 days

**Process:**
```bash
# 1. Generate new secret
NEW_SECRET=$(openssl rand -base64 32)

# 2. Add new version
echo -n "$NEW_SECRET" | gcloud secrets versions add jwt-secret \
  --data-file=- \
  --project=dentaflow-prod

# 3. Deploy with new secret
gcloud run deploy dentaflow-backend \
  --update-secrets=JWT_SECRET=jwt-secret:latest \
  --project=dentaflow-prod

# 4. Invalidate old tokens (users will need to re-login)
# This is automatic as old tokens will fail validation

# 5. Disable old version after 7 days
gcloud secrets versions disable <OLD_VERSION> --secret=jwt-secret
```

**External API Keys:**

**Frequency:** Manual (when compromised or annually)

**Process:**
1. Generate new key in external service (Stripe, Odoo, etc.)
2. Add to Secret Manager
3. Deploy with new key
4. Verify functionality
5. Revoke old key in external service
6. Destroy old secret version

---

## 7. Key Destruction

### 7.1 Scheduled Destruction

**Process:**
```bash
# 1. Disable secret version
gcloud secrets versions disable <VERSION> --secret=<SECRET_ID> --project=dentaflow-prod

# 2. Wait 30 days (grace period)

# 3. Destroy secret version
gcloud secrets versions destroy <VERSION> --secret=<SECRET_ID> --project=dentaflow-prod
```

**Audit:**
- All destruction events logged in Cloud Audit Logs
- Retention: 400 days (GCP default)

### 7.2 Emergency Destruction

**Scenario:** Key compromised

**Process:**
```bash
# 1. Immediately disable compromised key
gcloud secrets versions disable <VERSION> --secret=<SECRET_ID> --project=dentaflow-prod

# 2. Rotate to new key (see rotation procedures)

# 3. Destroy compromised key immediately (no grace period)
gcloud secrets versions destroy <VERSION> --secret=<SECRET_ID> --project=dentaflow-prod

# 4. Incident response (see INCIDENT_RESPONSE_PLAN.md)
```

---

## 8. Access Control

### 8.1 IAM Roles

| Role | Permissions | Who |
|------|-------------|-----|
| **secretmanager.admin** | Create, update, delete secrets | Eran Sarfaty (Security Officer) |
| **secretmanager.secretAccessor** | Read secret values | Cloud Run service account |
| **secretmanager.viewer** | List secrets (not values) | DevOps team |

### 8.2 Audit Logging

**Enabled Events:**
- Secret creation
- Secret access
- Secret version creation
- Secret version destruction
- Permission changes

**Retention:** 400 days (GCP default), then archived to Cloud Storage (7 years for HIPAA)

**Review:** Monthly by Security Officer

---

## 9. Backup and Recovery

### 9.1 Secret Backup

**Process:**
```bash
# Export all secrets (encrypted with GPG)
for secret in $(gcloud secrets list --format="value(name)" --project=dentaflow-prod); do
  gcloud secrets versions access latest --secret=$secret --project=dentaflow-prod | \
    gpg --encrypt --recipient eran@dentaflow.co.il > backups/${secret}.gpg
done

# Upload to secure storage
gsutil -m cp backups/*.gpg gs://dentaflow-secrets-backup/$(date +%Y%m%d)/
```

**Frequency:** Weekly  
**Retention:** 90 days  
**Storage:** GCS bucket with customer-managed encryption key (CMEK)

### 9.2 Secret Recovery

**Process:**
```bash
# Download backup
gsutil cp gs://dentaflow-secrets-backup/YYYYMMDD/<secret>.gpg /tmp/

# Decrypt
gpg --decrypt /tmp/<secret>.gpg > /tmp/<secret>

# Restore to Secret Manager
gcloud secrets versions add <secret> \
  --data-file=/tmp/<secret> \
  --project=dentaflow-prod

# Securely delete temp file
shred -vfz -n 10 /tmp/<secret>
```

---

## 10. Compliance Checklist

### 10.1 HIPAA Requirements

- [x] **§164.312(a)(2)(iv)** - Encryption and decryption
  - ✅ AES-256 for data at rest
  - ✅ TLS 1.2+ for data in transit
  - ✅ AES-128 for application-level PHI encryption

- [x] **§164.312(e)(2)(ii)** - Encryption
  - ✅ All ePHI encrypted at rest and in transit

- [ ] **§164.308(b)(1)** - Business associate contracts
  - ✅ GCP BAA signed
  - ⏳ Odoo BAA (pending)
  - ⏳ Stripe BAA (pending)

- [ ] **Key Management Best Practices**
  - ✅ Documented procedures
  - ⏳ Automated rotation (planned Week 2)
  - ⏳ GCP Secret Manager migration (planned Week 2)
  - ✅ Audit logging
  - ✅ Access control

### 10.2 Implementation Status

| Item | Status | Target Date |
|------|--------|-------------|
| **Current State** | ✅ Complete | - |
| - AES-128 PHI encryption | ✅ | - |
| - TLS 1.2+ in transit | ✅ | - |
| - Environment variable keys | ✅ | - |
| **Planned Migration** | ⏳ In Progress | Week 2 |
| - GCP Secret Manager setup | ⏳ | Week 2, Day 1-2 |
| - Application code update | ⏳ | Week 2, Day 3 |
| - Cloud Run deployment | ⏳ | Week 2, Day 4 |
| - Remove env vars | ⏳ | Week 2, Day 5 |
| **Future Enhancements** | 📅 Planned | Month 3-4 |
| - Automated key rotation | 📅 | Month 3 |
| - Customer-managed keys (CMEK) | 📅 | Month 4 |
| - Hardware security modules (HSM) | 📅 | Month 6 |

---

## 11. Incident Response

### 11.1 Key Compromise Scenarios

**Scenario 1: Encryption key exposed in logs**

```bash
# 1. Immediately rotate key
./scripts/rotate-encryption-key.sh --emergency

# 2. Review logs for unauthorized access
gcloud logging read "textPayload=~\"ENCRYPTION_KEY\"" \
  --limit=1000 --format=json --project=dentaflow-prod

# 3. Assess if PHI was accessed
python3 scripts/assess-phi-exposure.py --start-date=<DATE>

# 4. If breach confirmed, follow BREACH_NOTIFICATION_TEMPLATES.md
```

**Scenario 2: API key compromised**

```bash
# 1. Revoke key in external service (Stripe, Odoo, etc.)

# 2. Generate new key

# 3. Update Secret Manager
echo -n "$NEW_KEY" | gcloud secrets versions add <service>-api-key \
  --data-file=- --project=dentaflow-prod

# 4. Deploy with new key
gcloud run deploy dentaflow-backend \
  --update-secrets=<SERVICE>_API_KEY=<service>-api-key:latest \
  --project=dentaflow-prod

# 5. Monitor for unauthorized usage
```

---

## 12. Training and Awareness

### 12.1 Required Training

**All Developers:**
- Key management procedures (this document)
- Secure coding practices
- HIPAA encryption requirements

**Security Officer:**
- GCP Secret Manager administration
- Key rotation procedures
- Incident response

**Frequency:** Annually, or when procedures change

### 12.2 Security Reminders

- ❌ **NEVER** hardcode keys in source code
- ❌ **NEVER** commit keys to Git
- ❌ **NEVER** log keys or secrets
- ❌ **NEVER** send keys via email/chat
- ✅ **ALWAYS** use Secret Manager
- ✅ **ALWAYS** rotate keys on schedule
- ✅ **ALWAYS** report suspected compromise immediately

---

## 13. Monitoring and Alerts

### 13.1 Metrics to Monitor

```sql
-- Secret access frequency (should be stable)
SELECT 
  secret_id,
  COUNT(*) as access_count,
  COUNT(DISTINCT principal_email) as unique_users
FROM `dentaflow-prod.audit_logs.cloudaudit_googleapis_com_data_access`
WHERE resource.type = 'secretmanager.googleapis.com/Secret'
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY secret_id
ORDER BY access_count DESC;

-- Unusual access patterns
SELECT 
  principal_email,
  secret_id,
  COUNT(*) as access_count
FROM `dentaflow-prod.audit_logs.cloudaudit_googleapis_com_data_access`
WHERE resource.type = 'secretmanager.googleapis.com/Secret'
  AND timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY principal_email, secret_id
HAVING access_count > 100;
```

### 13.2 Alerts

**Configure alerts for:**
- Secret accessed by unauthorized principal
- Secret version destroyed
- Secret permission changed
- Unusual access frequency (>100/hour)

**Alert Channels:**
- Email: eran@dentaflow.co.il
- Slack: #dentaflow-security

---

## 14. References

- **HIPAA Security Rule:** 45 CFR § 164.312
- **NIST SP 800-57:** Recommendation for Key Management
- **GCP Secret Manager:** https://cloud.google.com/secret-manager/docs
- **GCP KMS:** https://cloud.google.com/kms/docs

---

**Document Control:**
- **Created:** October 18, 2025
- **Last Updated:** October 18, 2025
- **Next Review:** January 18, 2026
- **Owner:** Eran Sarfaty, Security Officer

---

*This document is confidential and proprietary to DentaFlow Ltd.*

