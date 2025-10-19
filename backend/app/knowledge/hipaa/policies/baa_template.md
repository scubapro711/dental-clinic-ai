# Business Associate Agreement (BAA)

**Between: [Dental Clinic Name] ("Covered Entity")**  
**And: DentaFlow SaaS Inc. ("Business Associate")**

**Effective Date:** [Date]

---

## RECITALS

WHEREAS, Covered Entity is a healthcare provider subject to the Health Insurance Portability and Accountability Act of 1996 ("HIPAA"), as amended, and its implementing regulations;

WHEREAS, Business Associate provides practice management software and AI-powered patient communication services to Covered Entity;

WHEREAS, in the course of providing such services, Business Associate may create, receive, maintain, or transmit Protected Health Information ("PHI") on behalf of Covered Entity;

WHEREAS, the parties wish to comply with HIPAA and ensure the protection of PHI;

NOW, THEREFORE, in consideration of the mutual covenants and agreements set forth herein, the parties agree as follows:

---

## 1. DEFINITIONS

**1.1. General Definitions**

Terms used but not otherwise defined in this Agreement shall have the meanings set forth in HIPAA and the HITECH Act.

**1.2. Specific Definitions**

- **"HIPAA"** means the Health Insurance Portability and Accountability Act of 1996, Public Law 104-191, as amended, and the regulations promulgated thereunder.

- **"HITECH Act"** means the Health Information Technology for Economic and Clinical Health Act, enacted as part of the American Recovery and Reinvestment Act of 2009, Public Law 111-5.

- **"PHI"** or **"Protected Health Information"** means individually identifiable health information that is transmitted or maintained in any form or medium by Business Associate on behalf of Covered Entity.

- **"Security Incident"** means the attempted or successful unauthorized access, use, disclosure, modification, or destruction of information or interference with system operations in an information system.

- **"Breach"** has the meaning given to such term under 45 CFR § 164.402.

---

## 2. OBLIGATIONS OF BUSINESS ASSOCIATE

**2.1. Permitted Uses and Disclosures**

Business Associate may use or disclose PHI only as permitted by this Agreement or as required by law. Specifically, Business Associate may:

(a) Use and disclose PHI to perform the services set forth in the Service Agreement;

(b) Use PHI for the proper management and administration of Business Associate;

(c) Disclose PHI as required by law;

(d) Use PHI to provide Data Aggregation services to Covered Entity;

(e) De-identify PHI in accordance with 45 CFR § 164.514(a)-(c).

**2.2. Prohibited Uses and Disclosures**

Business Associate shall not:

(a) Use or disclose PHI in any manner that would violate the HIPAA Privacy Rule if done by Covered Entity;

(b) Use or disclose PHI for marketing purposes without Covered Entity's prior written authorization;

(c) Sell PHI without Covered Entity's prior written authorization;

(d) Use or disclose PHI in a manner that constitutes an impermissible use or disclosure under the HIPAA Privacy Rule.

**2.3. Safeguards**

Business Associate shall implement and maintain appropriate administrative, physical, and technical safeguards to prevent the use or disclosure of PHI other than as provided for by this Agreement, in accordance with 45 CFR §§ 164.308, 164.310, and 164.312.

Specific safeguards include:

(a) **Encryption:** All PHI shall be encrypted in transit using TLS 1.3 and at rest using AES-256 encryption;

(b) **Access Controls:** Unique user identification, automatic logoff, and role-based access controls;

(c) **Audit Controls:** Comprehensive logging of all PHI access and modifications;

(d) **Integrity Controls:** Mechanisms to ensure PHI is not improperly altered or destroyed;

(e) **Transmission Security:** Secure transmission protocols for all PHI transfers.

**2.4. Reporting**

Business Associate shall report to Covered Entity:

(a) Any use or disclosure of PHI not provided for by this Agreement within 5 business days of becoming aware of such use or disclosure;

(b) Any Security Incident of which it becomes aware within 5 business days;

(c) Any Breach of Unsecured PHI without unreasonable delay and in no case later than 10 business days after discovery of the Breach.

Reports shall include:

- A brief description of what happened
- The date of the Breach and the date of discovery
- The types of PHI involved
- The number of individuals affected
- Steps taken to mitigate harm
- Contact information for questions

**2.5. Subcontractors**

Business Associate shall ensure that any subcontractors that create, receive, maintain, or transmit PHI on behalf of Business Associate agree to the same restrictions and conditions that apply to Business Associate with respect to such PHI, through a written agreement that meets the requirements of 45 CFR § 164.504(e).

Current subcontractors include:

- **Google Cloud Platform (GCP):** Infrastructure hosting (BAA on file)
- **Stripe, Inc.:** Payment processing (BAA on file)
- **Twilio Inc.:** SMS communications (BAA required)

**2.6. Access to PHI**

Business Associate shall provide access to PHI in a Designated Record Set to Covered Entity or, as directed by Covered Entity, to an Individual, in the time and manner designated by Covered Entity, to meet the requirements of 45 CFR § 164.524.

**2.7. Amendment of PHI**

Business Associate shall make any amendments to PHI in a Designated Record Set as directed by Covered Entity pursuant to 45 CFR § 164.526, within 10 business days of receiving such direction.

**2.8. Accounting of Disclosures**

Business Associate shall document all disclosures of PHI and information related to such disclosures as would be required for Covered Entity to respond to a request by an Individual for an accounting of disclosures in accordance with 45 CFR § 164.528.

Business Associate shall provide such information to Covered Entity or, as directed by Covered Entity, to an Individual, within 10 business days of a request.

**2.9. Availability of Books and Records**

Business Associate shall make its internal practices, books, and records relating to the use and disclosure of PHI available to the Secretary of the U.S. Department of Health and Human Services for purposes of determining Covered Entity's compliance with HIPAA.

**2.10. Minimum Necessary**

Business Associate shall request, use, and disclose only the minimum amount of PHI necessary to accomplish the intended purpose of the request, use, or disclosure, in accordance with 45 CFR § 164.502(b).

---

## 3. OBLIGATIONS OF COVERED ENTITY

**3.1. Permissible Requests**

Covered Entity shall not request Business Associate to use or disclose PHI in any manner that would not be permissible under the HIPAA Privacy Rule if done by Covered Entity.

**3.2. Notice of Privacy Practices**

Covered Entity shall provide Business Associate with a copy of its Notice of Privacy Practices and any changes thereto.

**3.3. Permission and Restrictions**

Covered Entity shall notify Business Associate of any:

(a) Changes in, or revocation of, permission by an Individual to use or disclose PHI;

(b) Restrictions on the use or disclosure of PHI that Covered Entity has agreed to in accordance with 45 CFR § 164.522.

**3.4. Permissible Uses and Disclosures**

Covered Entity shall obtain any necessary authorizations, consents, or permissions for Business Associate's use and disclosure of PHI as contemplated by this Agreement.

---

## 4. TERM AND TERMINATION

**4.1. Term**

This Agreement shall be effective as of the Effective Date and shall continue until terminated as provided herein or until the Service Agreement between the parties is terminated, whichever occurs first.

**4.2. Termination for Cause**

Either party may terminate this Agreement upon 30 days' written notice to the other party if the other party breaches a material term of this Agreement and fails to cure such breach within the 30-day notice period.

**4.3. Termination by Covered Entity**

Covered Entity may terminate this Agreement immediately upon written notice if:

(a) Business Associate has breached a material term of this Agreement and cure is not possible; or

(b) Covered Entity determines that Business Associate has violated a material term of this Agreement and termination is necessary to comply with HIPAA.

**4.4. Effect of Termination**

Upon termination of this Agreement for any reason, Business Associate shall:

(a) Return or destroy all PHI received from Covered Entity, or created or received by Business Associate on behalf of Covered Entity, that Business Associate still maintains in any form;

(b) Retain no copies of such PHI;

(c) Extend the protections of this Agreement to PHI retained by Business Associate for as long as such PHI is retained;

(d) If return or destruction is not feasible, provide notification of the conditions that make return or destruction infeasible and extend the protections of this Agreement to such PHI for as long as Business Associate retains such PHI.

**4.5. Data Retention Period**

Upon termination, Business Associate shall retain PHI for a period of 90 days to allow Covered Entity to retrieve data. After 90 days, all PHI shall be securely destroyed unless Covered Entity requests an extension in writing.

---

## 5. INDEMNIFICATION

**5.1. Indemnification by Business Associate**

Business Associate shall indemnify, defend, and hold harmless Covered Entity from and against any and all claims, losses, liabilities, costs, and expenses (including reasonable attorneys' fees) arising out of or resulting from:

(a) Any breach by Business Associate of its obligations under this Agreement;

(b) Any negligent or wrongful act or omission by Business Associate in connection with its performance under this Agreement;

(c) Any Breach of Unsecured PHI caused by Business Associate's failure to implement appropriate safeguards.

**5.2. Limitation of Liability**

Notwithstanding the foregoing, Business Associate's total liability under this Agreement shall not exceed the total fees paid by Covered Entity to Business Associate in the 12 months preceding the claim, except in cases of gross negligence or willful misconduct.

---

## 6. MISCELLANEOUS

**6.1. Regulatory References**

A reference in this Agreement to a section in HIPAA or the HITECH Act means the section as in effect or as amended, and for which compliance is required.

**6.2. Amendment**

The parties agree to take such action as is necessary to amend this Agreement from time to time as is necessary for Covered Entity or Business Associate to comply with the requirements of HIPAA, the HITECH Act, and their implementing regulations.

**6.3. Survival**

The obligations of Business Associate under Sections 2.3 (Safeguards), 2.4 (Reporting), and 4.4 (Effect of Termination) shall survive the termination of this Agreement.

**6.4. Interpretation**

Any ambiguity in this Agreement shall be resolved in favor of a meaning that permits Covered Entity to comply with HIPAA and the HITECH Act.

**6.5. Entire Agreement**

This Agreement, together with the Service Agreement, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior agreements and understandings, whether written or oral.

**6.6. Governing Law**

This Agreement shall be governed by and construed in accordance with the laws of [State], without regard to its conflict of laws principles.

**6.7. Notices**

All notices required or permitted under this Agreement shall be in writing and delivered by email or certified mail to:

**For Covered Entity:**  
[Clinic Name]  
[Address]  
[Email]

**For Business Associate:**  
DentaFlow SaaS Inc.  
[Address]  
Email: legal@dentaflow.ai

---

## SIGNATURES

**COVERED ENTITY:**

[Dental Clinic Name]

By: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
Name: [Print Name]  
Title: [Title]  
Date: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**BUSINESS ASSOCIATE:**

DentaFlow SaaS Inc.

By: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_  
Name: [Print Name]  
Title: Chief Executive Officer  
Date: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## EXHIBIT A: TECHNICAL AND ORGANIZATIONAL MEASURES

Business Associate implements the following technical and organizational measures to protect PHI:

### A.1. Access Control

- Unique user IDs for all users
- Strong password requirements (minimum 8 characters, complexity requirements)
- Multi-factor authentication available
- Automatic session timeout after 24 hours of inactivity
- Role-based access control (RBAC)

### A.2. Audit Controls

- Comprehensive logging of all PHI access
- Logs retained for 6 years
- Regular log review and analysis
- Automated alerting for suspicious activity

### A.3. Integrity Controls

- Database constraints and validation
- Checksums for data verification
- Version control for all code changes

### A.4. Transmission Security

- TLS 1.3 encryption for all data in transit
- HTTPS enforced for all web traffic
- Secure API authentication using JWT tokens

### A.5. Encryption

- AES-256 encryption for data at rest
- Encrypted database backups
- Encrypted file storage

### A.6. Physical Safeguards

- Data hosted in SOC 2 Type II certified GCP data centers
- Physical access controls managed by GCP
- Environmental controls (fire suppression, climate control)

### A.7. Organizational Measures

- Designated Security Official
- Annual security training for all employees
- Background checks for employees with PHI access
- Confidentiality agreements with all employees
- Incident response procedures
- Business continuity and disaster recovery plans

### A.8. Backup and Recovery

- Daily automated backups
- 7-day backup retention
- Quarterly disaster recovery testing
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour

