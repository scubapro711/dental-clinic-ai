# HIPAA Breach Notification Rule Summary

**Regulation:** 45 CFR Part 164, Subpart D  
**Effective Date:** September 23, 2009  
**Last Updated:** January 2013 (Omnibus Rule)  
**Category:** regulations  
**Critical:** true

---

## Overview

The HIPAA Breach Notification Rule requires covered entities and business associates to provide notification following a breach of unsecured protected health information.

The Rule establishes the framework for determining when a breach has occurred and the required notifications to affected individuals, HHS, and in some cases, the media.

---

## Key Definitions

### Breach

The acquisition, access, use, or disclosure of PHI in a manner not permitted under the Privacy Rule that compromises the security or privacy of the PHI.

**Key Elements:**
1. Impermissible acquisition, access, use, or disclosure
2. Under the Privacy Rule
3. Compromises security or privacy of PHI

### Unsecured PHI

PHI that is not rendered unusable, unreadable, or indecipherable to unauthorized persons through:
- **Encryption:** NIST-compliant encryption
- **Destruction:** Shredding, burning, pulverizing, or purging

**If PHI is properly encrypted, breach notification may NOT be required.**

---

## Breach Determination

### Step 1: Was there an impermissible use or disclosure?

**Exceptions (NOT a breach):**
1. **Unintentional acquisition/access** by workforce member acting in good faith within scope of authority
2. **Inadvertent disclosure** from authorized person to another authorized person at same organization
3. **Good faith belief** that unauthorized person could not have retained the information

### Step 2: Risk Assessment (Required)

If not an exception, must conduct risk assessment considering:

1. **Nature and extent of PHI**
   - Types of identifiers
   - Likelihood of re-identification

2. **Unauthorized person**
   - Who obtained the PHI?
   - Relationship to covered entity?

3. **Was PHI actually acquired or viewed?**
   - Or just potentially accessed?

4. **Extent of mitigation**
   - What steps were taken to mitigate harm?

**If low probability of compromise → NOT a breach**  
**If NOT low probability → IS a breach → Notification required**

---

## Notification Requirements

### 1. Individual Notification (Required)

**Timeline:** Within **60 days** of discovery

**Method:**
- **First-class mail** to last known address
- **Email** if individual agreed to electronic notice
- **Substitute notice** if contact information insufficient:
  - Conspicuous posting on website for 90 days, OR
  - Notice in major media if 10+ individuals in same state

**Content Must Include:**
1. Brief description of what happened
2. Types of PHI involved
3. Steps individuals should take to protect themselves
4. What entity is doing to investigate and mitigate
5. Contact procedures for questions

**Sample Letter Template:**
```
[Date]

Dear [Individual Name],

We are writing to notify you of a breach that may have affected the security of your protected health information (PHI).

What Happened:
[Brief description of incident, date of breach, date of discovery]

What Information Was Involved:
[Types of PHI: name, SSN, medical records, etc.]

What We Are Doing:
[Steps taken to investigate, mitigate, and prevent future incidents]

What You Can Do:
[Recommendations: monitor accounts, credit monitoring, etc.]

For More Information:
[Contact name, phone, email]

Sincerely,
[Organization Name]
```

---

### 2. HHS Notification (Required)

#### Breaches Affecting 500+ Individuals

**Timeline:** Within **60 days** of discovery

**Method:** Online submission to HHS Office for Civil Rights (OCR)

**Portal:** https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf

**Result:** Posted on HHS "Wall of Shame" (public breach portal)

#### Breaches Affecting <500 Individuals

**Timeline:** Within **60 days** of end of calendar year

**Method:** Annual log submission to HHS

---

### 3. Media Notification (Sometimes Required)

**Required if:** Breach affects **500+ individuals** in same state or jurisdiction

**Timeline:** Within **60 days** of discovery

**Method:** Prominent media outlets serving the state/jurisdiction

---

### 4. Business Associate Notification

**If Business Associate discovers breach:**

**Timeline:** Within **60 days** of discovery (or per BAA)

**Method:** Notify covered entity

**Content:** All information necessary for covered entity to meet notification requirements

---

## Breach Discovery

**Discovery Date** = First day breach is known or should have been known

**Presumption:** Breach discovered within **30 days** unless documented otherwise

**Burden of Proof:** On covered entity to prove later discovery date

---

## Penalties for Non-Compliance

### Civil Penalties

Same tiered structure as Privacy/Security Rules:

| Violation Category | Minimum Penalty | Maximum Penalty |
|-------------------|-----------------|-----------------|
| Unknowing | $100 per violation | $50,000 per violation |
| Reasonable cause | $1,000 per violation | $50,000 per violation |
| Willful neglect (corrected) | $10,000 per violation | $50,000 per violation |
| Willful neglect (not corrected) | $50,000 per violation | $50,000 per violation |

**Annual maximum:** $1.5 million per violation category

### Additional Consequences

- **Reputation damage** - Public breach portal
- **Lawsuits** - Class action from affected individuals
- **State penalties** - Additional state breach laws
- **Loss of trust** - Patients may leave practice

---

## Common Breach Scenarios

### 1. Lost/Stolen Devices

**Scenario:** Laptop with patient records stolen from car

**Breach?**
- **If encrypted:** NO (safe harbor)
- **If not encrypted:** YES → Notification required

**Prevention:**
- Encrypt all devices
- Use mobile device management
- Don't leave devices in vehicles

---

### 2. Unauthorized Access

**Scenario:** Employee accesses ex-spouse's medical record

**Breach?** YES (unauthorized access)

**Notification:** Required

**Prevention:**
- Monitor audit logs
- Implement access controls
- Train workforce on appropriate access

---

### 3. Misdirected Email/Fax

**Scenario:** Email with PHI sent to wrong recipient

**Breach?** Depends on risk assessment
- **To another healthcare provider:** Likely NO (exception)
- **To random person:** Likely YES

**Prevention:**
- Encrypt email
- Verify recipient before sending
- Use secure messaging

---

### 4. Hacking/Ransomware

**Scenario:** Ransomware encrypts patient database

**Breach?** YES (presumed unless proven otherwise)

**Notification:** Required (usually 500+)

**Prevention:**
- Regular backups
- Security updates
- Firewall and antivirus
- Security awareness training

---

### 5. Improper Disposal

**Scenario:** Patient records thrown in regular trash

**Breach?** Depends on risk assessment
- **Likely YES** if dumpster accessible

**Prevention:**
- Shred all PHI
- Secure disposal vendor
- Document disposal

---

### 6. Business Associate Breach

**Scenario:** Billing company has data breach

**Breach?** YES

**Notification:** Business associate notifies covered entity → Covered entity notifies individuals

**Prevention:**
- Strong BAA
- Vendor security assessment
- Regular audits

---

## Breach Response Checklist

### Immediate (Within 24 hours)

- [ ] **Contain** the breach (stop ongoing disclosure)
- [ ] **Document** everything (date, time, what happened)
- [ ] **Notify** leadership and Privacy/Security Officer
- [ ] **Preserve** evidence (logs, emails, etc.)

### Short-term (Within 7 days)

- [ ] **Investigate** the incident thoroughly
- [ ] **Risk Assessment** (required)
  - [ ] Nature and extent of PHI
  - [ ] Who accessed it?
  - [ ] Was it actually viewed?
  - [ ] Mitigation efforts
- [ ] **Determine** if breach notification required
- [ ] **Mitigate** harm (password resets, credit monitoring)
- [ ] **Notify** business associates if applicable

### Medium-term (Within 60 days)

- [ ] **Individual Notification** (if breach)
- [ ] **HHS Notification** (if 500+)
- [ ] **Media Notification** (if 500+ in same state)
- [ ] **Document** all notifications sent
- [ ] **Implement** corrective actions

### Long-term (Ongoing)

- [ ] **Review** and update policies
- [ ] **Retrain** workforce
- [ ] **Monitor** for additional incidents
- [ ] **Annual log** to HHS (if <500)

---

## DentaFlow Breach Response

### Prevention

- **Encryption:** All ePHI encrypted (AES-256)
- **Access Controls:** Role-based access
- **Audit Logging:** All access logged
- **Monitoring:** Automated security alerts
- **Training:** Annual HIPAA training

### Detection

- **Automated Alerts:** Suspicious activity triggers alerts
- **Log Monitoring:** Daily review of audit logs
- **Incident Reporting:** Easy reporting mechanism
- **Security Scans:** Weekly vulnerability scans

### Response

- **Incident Response Plan:** Documented procedures
- **Response Team:** Designated security officer
- **Risk Assessment Tool:** Automated risk assessment
- **Notification Templates:** Pre-approved templates
- **HHS Portal Integration:** Direct submission capability

### Documentation

- **Incident Log:** All incidents documented
- **Risk Assessments:** Stored securely
- **Notifications:** Copies of all notifications
- **Mitigation:** Actions taken documented

---

## Safe Harbor: Encryption

### Encryption Standards (NIST)

**At Rest:**
- AES-256 (Advanced Encryption Standard)
- Full disk encryption
- Database encryption
- File-level encryption

**In Transit:**
- TLS 1.2 or higher
- HTTPS
- VPN
- Encrypted email (S/MIME, PGP)

### Key Management

- **Separate** encryption keys from data
- **Rotate** keys regularly
- **Secure** key storage (HSM, key vault)
- **Access control** for keys

### If Encrypted

**Breach notification NOT required if:**
- PHI encrypted per NIST standards
- Encryption key NOT compromised
- Document encryption in risk assessment

---

## Reporting to HHS

### Online Portal

https://ocrportal.hhs.gov/ocr/breach/wizard_breach.jsf

### Information Required

1. Name of covered entity
2. Contact information
3. Business associate involved (if applicable)
4. Date of breach
5. Date of discovery
6. Number of individuals affected
7. Type of breach
8. Location of breach
9. Types of PHI involved
10. Brief description
11. Safeguards in place
12. Mitigation efforts

### Public Breach Portal

All breaches affecting 500+ individuals posted publicly:
https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf

**"Wall of Shame"** - searchable by organization name

---

## Best Practices

1. **Encrypt everything** - Safe harbor protection
2. **Conduct risk assessments** - Document thoroughly
3. **Respond quickly** - 60-day deadline
4. **Document everything** - Burden of proof on you
5. **Have incident response plan** - Test annually
6. **Train workforce** - Recognize and report breaches
7. **Monitor continuously** - Detect breaches early
8. **Review BAAs** - Ensure notification requirements
9. **Maintain breach log** - Track all incidents
10. **Learn from breaches** - Implement corrective actions

---

## References

- 45 CFR Part 164, Subpart D
- HHS Breach Notification Rule: https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html
- OCR Breach Portal: https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf
- NIST Encryption Standards: https://csrc.nist.gov/publications

---

**Last Verified:** October 2025  
**Next Review:** April 2026

