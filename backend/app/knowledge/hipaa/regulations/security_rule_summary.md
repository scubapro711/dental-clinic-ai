# HIPAA Security Rule Summary

**Regulation:** 45 CFR Part 164, Subpart C  
**Effective Date:** April 20, 2005  
**Last Updated:** January 2013 (Omnibus Rule)  
**Category:** regulations  
**Critical:** true

---

## Overview

The HIPAA Security Rule establishes national standards to protect electronic protected health information (ePHI) that is created, received, used, or maintained by covered entities and business associates.

The Security Rule requires appropriate administrative, physical, and technical safeguards to ensure the confidentiality, integrity, and availability of ePHI.

---

## Key Definitions

### Electronic Protected Health Information (ePHI)

PHI that is:
- Transmitted by electronic media
- Maintained in electronic media
- Includes information in electronic storage devices

**Examples:**
- EHR/EMR systems
- Email containing PHI
- Databases with patient information
- Backup tapes
- Cloud storage
- Mobile devices

### Security vs. Privacy

- **Privacy Rule:** Protects ALL PHI (paper, electronic, oral)
- **Security Rule:** Protects only ePHI

---

## The Three Safeguards

### 1. Administrative Safeguards (§164.308)

Policies and procedures to manage security measures.

#### Required Standards:

**Security Management Process**
- Risk Analysis (R)
- Risk Management (R)
- Sanction Policy (R)
- Information System Activity Review (R)

**Assigned Security Responsibility (R)**
- Designate a Security Officer

**Workforce Security**
- Authorization/Supervision (A)
- Workforce Clearance (A)
- Termination Procedures (A)

**Information Access Management**
- Isolating Healthcare Clearinghouse Functions (R)
- Access Authorization (A)
- Access Establishment and Modification (A)

**Security Awareness and Training**
- Security Reminders (A)
- Protection from Malicious Software (A)
- Log-in Monitoring (A)
- Password Management (A)

**Security Incident Procedures (R)**
- Response and Reporting

**Contingency Plan (R)**
- Data Backup Plan (R)
- Disaster Recovery Plan (R)
- Emergency Mode Operation Plan (R)
- Testing and Revision (A)
- Applications and Data Criticality Analysis (A)

**Evaluation (R)**
- Periodic technical and non-technical evaluation

**Business Associate Contracts (R)**
- Written contract or other arrangement

**(R) = Required, (A) = Addressable**

---

### 2. Physical Safeguards (§164.310)

Physical measures to protect electronic systems and buildings.

#### Required Standards:

**Facility Access Controls**
- Contingency Operations (A)
- Facility Security Plan (A)
- Access Control and Validation (A)
- Maintenance Records (A)

**Workstation Use (R)**
- Policies for workstation functions

**Workstation Security (R)**
- Physical safeguards for workstations

**Device and Media Controls**
- Disposal (R)
- Media Re-use (R)
- Accountability (A)
- Data Backup and Storage (A)

---

### 3. Technical Safeguards (§164.312)

Technology to protect ePHI and control access.

#### Required Standards:

**Access Control (R)**
- Unique User Identification (R)
- Emergency Access Procedure (R)
- Automatic Logoff (A)
- Encryption and Decryption (A)

**Audit Controls (R)**
- Hardware, software, and/or procedural mechanisms to record and examine activity

**Integrity**
- Mechanism to Authenticate ePHI (A)

**Person or Entity Authentication (R)**
- Verify identity of person or entity

**Transmission Security**
- Integrity Controls (A)
- Encryption (A)

---

## Required vs. Addressable

### Required Specifications

MUST be implemented as specified.

### Addressable Specifications

Must:
1. **Assess** whether reasonable and appropriate
2. **Implement** if reasonable and appropriate
3. **Document** why not implemented if not reasonable
4. **Implement** equivalent alternative if available

**Addressable ≠ Optional!**

---

## Risk Analysis (Critical Requirement)

Must conduct an accurate and thorough assessment of potential risks and vulnerabilities to ePHI.

### Steps:

1. **Scope** - Define boundaries (systems, facilities, ePHI)
2. **Data Collection** - Identify where ePHI is stored, transmitted, processed
3. **Identify Threats** - Natural, human, environmental
4. **Identify Vulnerabilities** - Weaknesses that could be exploited
5. **Assess Current Security** - What safeguards exist?
6. **Determine Likelihood** - Probability of threat occurrence
7. **Determine Impact** - Potential harm if threat occurs
8. **Determine Risk Level** - Combine likelihood and impact
9. **Finalize Documentation** - Document findings
10. **Periodic Review** - Update regularly

---

## Encryption

### Is Encryption Required?

**No**, but it is **addressable** for:
- Access Control (§164.312(a)(2)(iv))
- Transmission Security (§164.312(e)(2)(ii))

### Safe Harbor

If ePHI is encrypted per NIST standards, breach notification may not be required (if encryption key not compromised).

### Best Practice

**Encrypt:**
- Data at rest (databases, backups, devices)
- Data in transit (email, file transfers, APIs)
- Mobile devices and laptops
- Backup media

---

## Business Associate Requirements

Business associates must:
- Comply with Security Rule safeguards
- Implement administrative, physical, and technical safeguards
- Report security incidents to covered entity
- Ensure subcontractors comply

---

## Penalties for Non-Compliance

Same as Privacy Rule:

| Violation Category | Minimum Penalty | Maximum Penalty |
|-------------------|-----------------|-----------------|
| Unknowing | $100 per violation | $50,000 per violation |
| Reasonable cause | $1,000 per violation | $50,000 per violation |
| Willful neglect (corrected) | $10,000 per violation | $50,000 per violation |
| Willful neglect (not corrected) | $50,000 per violation | $50,000 per violation |

**Annual maximum:** $1.5 million per violation category

---

## Dental Practice Security Checklist

### Administrative

- [ ] Designate Security Officer
- [ ] Conduct annual risk analysis
- [ ] Implement security policies and procedures
- [ ] Train all workforce members
- [ ] Review and update policies annually
- [ ] Have Business Associate Agreements
- [ ] Implement sanction policy
- [ ] Review audit logs regularly

### Physical

- [ ] Lock server rooms and file cabinets
- [ ] Secure workstations (lock screens)
- [ ] Control facility access (badges, keys)
- [ ] Dispose of ePHI securely (shred, wipe)
- [ ] Implement workstation use policies
- [ ] Maintain device inventory
- [ ] Secure mobile devices

### Technical

- [ ] Unique user IDs for all users
- [ ] Strong password policies
- [ ] Automatic logoff after inactivity
- [ ] Encrypt ePHI (at rest and in transit)
- [ ] Implement audit logging
- [ ] Use firewalls and antivirus
- [ ] Regular software updates
- [ ] Secure remote access (VPN)
- [ ] Multi-factor authentication

### Contingency Planning

- [ ] Daily data backups
- [ ] Test backup restoration
- [ ] Disaster recovery plan
- [ ] Emergency mode operation plan
- [ ] Test contingency plans annually

---

## DentaFlow Security Implementation

### Administrative Safeguards

- **Security Officer:** Designated in Super Admin
- **Risk Analysis:** Automated quarterly scans
- **Training:** Annual HIPAA training required
- **Incident Response:** Automated detection and reporting
- **Business Associates:** BAA management system

### Physical Safeguards

- **Cloud Infrastructure:** Google Cloud Platform (SOC 2 certified)
- **Data Centers:** Multiple regions with physical security
- **Workstation Security:** Session timeout after 15 minutes
- **Device Controls:** Mobile device management policies

### Technical Safeguards

- **Access Control:** Role-based access (RBAC)
- **Unique User IDs:** Required for all users
- **Encryption:** AES-256 at rest, TLS 1.3 in transit
- **Audit Logs:** All ePHI access logged
- **Authentication:** Multi-factor authentication (MFA)
- **Automatic Logoff:** 15 minutes of inactivity
- **Transmission Security:** HTTPS, encrypted APIs

### Contingency Planning

- **Backups:** Automated daily backups
- **Disaster Recovery:** 99.95% uptime SLA
- **Emergency Access:** Designated emergency procedures
- **Testing:** Quarterly disaster recovery tests

---

## Common Security Violations

1. **Lack of Risk Analysis** - Most common violation
2. **No Encryption** - Especially for mobile devices
3. **Weak Passwords** - No password policy
4. **No Audit Logs** - Can't track ePHI access
5. **Unsecured Devices** - Lost/stolen laptops, phones
6. **No BAAs** - Missing business associate agreements
7. **No Training** - Workforce not trained on security
8. **Outdated Software** - Unpatched vulnerabilities

---

## Best Practices

1. **Conduct annual risk analysis**
2. **Encrypt all ePHI** (at rest and in transit)
3. **Implement MFA** for all users
4. **Regular security training** (at least annually)
5. **Monitor audit logs** for suspicious activity
6. **Patch systems regularly** (monthly at minimum)
7. **Test backups** (quarterly)
8. **Review BAAs** (annually)
9. **Incident response plan** (test annually)
10. **Document everything** (policies, training, incidents)

---

## References

- 45 CFR Part 164, Subpart C
- HHS Security Rule Summary: https://www.hhs.gov/hipaa/for-professionals/security/index.html
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- OCR Security Risk Assessment Tool: https://www.healthit.gov/topic/privacy-security-and-hipaa/security-risk-assessment-tool

---

**Last Verified:** October 2025  
**Next Review:** April 2026

