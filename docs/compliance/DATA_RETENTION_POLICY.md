# Data Retention and Deletion Policy
**DentaFlow - HIPAA-Compliant Data Management**  
**Version:** 1.0  
**Effective Date:** October 19, 2025  
**Last Updated:** October 19, 2025  
**Owner:** Privacy Officer

---

## 1. Executive Summary

This Data Retention and Deletion Policy establishes DentaFlow's approach to managing Protected Health Information (PHI) and other sensitive data throughout its lifecycle, ensuring compliance with HIPAA regulations, state laws, and industry best practices.

**Purpose:** Define retention periods, deletion procedures, and data lifecycle management to balance legal/regulatory requirements, business needs, and privacy principles.

**Scope:** All data collected, processed, or stored by DentaFlow, including PHI, business records, system logs, and backups.

**Key Principles:**
- Retain data only as long as necessary for business, legal, or regulatory purposes
- Securely delete data when retention period expires
- Maintain data integrity and availability during retention period
- Document all retention and deletion activities
- Comply with HIPAA, state laws, and contractual obligations

---

## 2. Regulatory Framework

### 2.1 HIPAA Requirements

**HIPAA Privacy Rule (45 CFR § 164.530(j)):**
- Covered entities must retain documentation of HIPAA policies, procedures, and communications for **6 years** from creation or last effective date
- No specific retention period mandated for medical records themselves (defer to state laws)

**HIPAA Security Rule (45 CFR § 164.316(b)(2)):**
- Security documentation must be retained for **6 years**
- Includes policies, procedures, security incident logs, and risk assessments

### 2.2 State Laws

Dental record retention requirements vary by state. DentaFlow will comply with the **most stringent** applicable state law.

**Common State Requirements:**
- **Adult patients:** 7-10 years from last treatment
- **Minor patients:** Until age of majority + 7-10 years
- **Deceased patients:** 3-7 years after death

**DentaFlow Standard:** **10 years** from last patient encounter (covers most states)

### 2.3 Other Regulations

**IRS Requirements:**
- Financial records: **7 years**
- Tax returns: **7 years**
- Employment tax records: **4 years**

**State Business Laws:**
- Business records: Typically **7 years**
- Contracts: Duration of contract + **7 years**

**Statute of Limitations:**
- Medical malpractice: Varies by state (2-10 years)
- Breach of contract: Typically **6 years**

---

## 3. Data Classification

DentaFlow categorizes data into four tiers based on sensitivity and regulatory requirements:

### Tier 1: Protected Health Information (PHI)

**Definition:** Individually identifiable health information created, received, maintained, or transmitted by DentaFlow.

**Examples:**
- Patient demographics (name, address, DOB, SSN)
- Medical/dental history
- Treatment plans and clinical notes
- Appointment records
- Insurance information
- Payment information
- Diagnostic images (X-rays, photos)
- Lab results
- Prescriptions
- Communication with patients about health matters

**Retention Period:** **10 years** from last patient encounter

**Special Cases:**
- **Minor patients:** Until age 21 (or state age of majority) + 10 years
- **Deceased patients:** 10 years from date of death
- **Litigation hold:** Indefinitely until hold is lifted

### Tier 2: Business Records

**Definition:** Non-PHI business and operational data.

**Examples:**
- Financial records (invoices, receipts, ledgers)
- Contracts and agreements
- Employee records (non-medical)
- Vendor agreements
- Marketing materials
- Business correspondence

**Retention Period:** **7 years** from creation or last activity

**Special Cases:**
- **Tax returns:** 7 years from filing
- **Contracts:** Duration + 7 years
- **Employee records:** 7 years from termination

### Tier 3: System Logs and Audit Trails

**Definition:** Technical logs and audit records for security, compliance, and troubleshooting.

**Examples:**
- Application logs
- Database query logs
- Access logs (PHI access tracking)
- Authentication logs
- Security incident logs
- Backup logs
- System performance logs

**Retention Period:**
- **PHI access logs:** **6 years** (HIPAA requirement)
- **Security logs:** **6 years** (HIPAA requirement)
- **Application logs:** **1 year** (operational)
- **Performance logs:** **90 days** (operational)

### Tier 4: Temporary Data

**Definition:** Data needed only for short-term operational purposes.

**Examples:**
- Session data
- Cache data
- Temporary files
- Email notifications (sent)
- SMS notifications (sent)
- Unconfirmed user registrations

**Retention Period:** **30-90 days** or until purpose fulfilled

---

## 4. Retention Schedule Matrix

| Data Type | Category | Retention Period | Trigger | Legal Basis |
|-----------|----------|------------------|---------|-------------|
| **Patient Medical Records** | PHI | 10 years | Last encounter | State laws |
| **Patient Demographics** | PHI | 10 years | Last encounter | State laws |
| **Appointment History** | PHI | 10 years | Last encounter | State laws |
| **Treatment Plans** | PHI | 10 years | Last encounter | State laws |
| **Clinical Notes** | PHI | 10 years | Last encounter | State laws |
| **Diagnostic Images** | PHI | 10 years | Last encounter | State laws |
| **Lab Results** | PHI | 10 years | Last encounter | State laws |
| **Insurance Information** | PHI | 10 years | Last encounter | State laws |
| **Payment Records** | PHI | 10 years | Last encounter | State laws + IRS |
| **Patient Communications** | PHI | 10 years | Last encounter | State laws |
| **Minor Patient Records** | PHI | Age 21 + 10 years | Last encounter | State laws |
| **Deceased Patient Records** | PHI | 10 years | Date of death | State laws |
| **HIPAA Policies** | Business | 6 years | Last effective date | HIPAA |
| **Security Policies** | Business | 6 years | Last effective date | HIPAA |
| **Risk Assessments** | Business | 6 years | Completion date | HIPAA |
| **Security Incidents** | Business | 6 years | Incident date | HIPAA |
| **PHI Access Logs** | Audit | 6 years | Log date | HIPAA |
| **Authentication Logs** | Audit | 6 years | Log date | HIPAA |
| **Financial Records** | Business | 7 years | Transaction date | IRS |
| **Tax Returns** | Business | 7 years | Filing date | IRS |
| **Contracts** | Business | Duration + 7 years | Contract end | State law |
| **Employee Records** | Business | 7 years | Termination date | State law |
| **Vendor Agreements** | Business | Duration + 7 years | Agreement end | State law |
| **Business Correspondence** | Business | 7 years | Creation date | Best practice |
| **Application Logs** | Audit | 1 year | Log date | Operational |
| **Performance Logs** | Audit | 90 days | Log date | Operational |
| **Session Data** | Temporary | 30 days | Session end | Operational |
| **Cache Data** | Temporary | 7 days | Creation date | Operational |
| **Unconfirmed Registrations** | Temporary | 30 days | Registration date | Operational |
| **Email Notifications (sent)** | Temporary | 90 days | Send date | Operational |
| **SMS Notifications (sent)** | Temporary | 90 days | Send date | Operational |
| **Backup Data** | All | 30 days | Backup date | Operational |
| **Point-in-Time Recovery** | All | 7 days | Transaction date | Operational |

---

## 5. Data Lifecycle Management

### 5.1 Data Creation & Collection

**Principles:**
- Collect only data necessary for business purposes
- Obtain appropriate consent
- Document data source and purpose
- Apply appropriate classification

**Implementation:**
- Data classification tags in database
- Purpose documentation in data dictionary
- Consent tracking in patient records

### 5.2 Data Storage & Maintenance

**Principles:**
- Store data securely based on classification
- Maintain data integrity and availability
- Implement access controls
- Regular backups

**Implementation:**
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)
- Role-based access control (RBAC)
- Daily automated backups
- Multi-region storage for critical data

### 5.3 Data Use & Access

**Principles:**
- Access only for legitimate business purposes
- Minimum necessary access
- Audit all PHI access
- Secure data in use

**Implementation:**
- Audit logging for all PHI access
- Just-in-time access provisioning
- Data masking for non-clinical users
- Secure workstations

### 5.4 Data Retention

**Principles:**
- Retain data per retention schedule
- Maintain data integrity during retention
- Review retention periods annually
- Litigation hold process

**Implementation:**
- Automated retention period tracking
- Quarterly retention review
- Legal hold flags in database
- Retention period metadata

### 5.5 Data Deletion

**Principles:**
- Securely delete data when retention period expires
- Verify deletion completeness
- Document all deletions
- Irreversible deletion methods

**Implementation:**
- Automated deletion workflows
- Cryptographic erasure (key deletion)
- Deletion audit logs
- Deletion verification reports

---

## 6. Deletion Procedures

### 6.1 Automated Deletion Process

**Frequency:** Monthly (first Sunday of each month at 2:00 AM UTC)

**Process:**
1. **Identification Phase**
   - Query database for records past retention period
   - Exclude records with litigation hold flag
   - Generate deletion candidate list
   - Send notification to Privacy Officer

2. **Review Phase** (48-hour window)
   - Privacy Officer reviews deletion list
   - Check for any holds or exceptions
   - Approve or reject deletions
   - Document review decision

3. **Deletion Phase**
   - Execute approved deletions
   - Delete from primary database
   - Delete from backups (>30 days old)
   - Delete encryption keys (cryptographic erasure)
   - Delete from search indexes
   - Delete from caches

4. **Verification Phase**
   - Verify deletion completeness
   - Generate deletion report
   - Archive deletion logs
   - Notify Privacy Officer of completion

5. **Audit Phase**
   - Review deletion logs
   - Verify compliance with policy
   - Document any issues
   - Update retention metrics

**Technical Implementation:**
```python
# Pseudocode for automated deletion
def monthly_deletion_job():
    # 1. Identify candidates
    candidates = identify_expired_records()
    candidates = exclude_litigation_holds(candidates)
    
    # 2. Notify for review
    send_review_notification(privacy_officer, candidates)
    
    # Wait 48 hours for review
    wait_for_approval(hours=48)
    
    # 3. Execute deletions
    approved = get_approved_deletions()
    for record in approved:
        delete_from_database(record)
        delete_from_backups(record)
        delete_encryption_keys(record)
        delete_from_indexes(record)
        log_deletion(record)
    
    # 4. Verify and report
    verify_deletions(approved)
    generate_deletion_report()
    notify_completion(privacy_officer)
```

### 6.2 Manual Deletion Process

**Triggers:**
- Patient request (Right to Erasure)
- Legal hold lift
- Business decision
- Data correction requiring deletion

**Process:**
1. **Request Submission**
   - Requester submits deletion request via ticketing system
   - Includes: Data subject, reason, scope, urgency

2. **Authorization**
   - Privacy Officer reviews request
   - Verifies requester authority
   - Checks for legal/regulatory barriers
   - Approves or denies request

3. **Execution**
   - Authorized personnel execute deletion
   - Follow same technical steps as automated process
   - Document all actions

4. **Verification**
   - Verify deletion completeness
   - Generate deletion certificate
   - Notify requester of completion

5. **Audit**
   - Log deletion in audit trail
   - Archive deletion documentation
   - Update data inventory

**Timeline:**
- Standard requests: Within 30 days
- Urgent requests: Within 5 business days
- Patient requests: Within 30 days (GDPR-aligned)

### 6.3 Secure Deletion Methods

**Database Records:**
- **Method:** Cryptographic erasure (delete encryption keys)
- **Rationale:** Renders data unrecoverable without keys
- **Verification:** Attempt decryption (should fail)

**Backups:**
- **Method:** Overwrite with random data (3-pass)
- **Rationale:** Prevents recovery from backup media
- **Verification:** Read-back verification

**File Storage:**
- **Method:** Secure delete (DoD 5220.22-M standard)
- **Rationale:** Overwrites data multiple times
- **Verification:** File recovery attempt (should fail)

**Logs:**
- **Method:** Truncation + overwrite
- **Rationale:** Removes sensitive data from logs
- **Verification:** Log search for deleted data (should return no results)

**Caches:**
- **Method:** Cache invalidation + purge
- **Rationale:** Removes data from memory/disk caches
- **Verification:** Cache query (should return no results)

---

## 7. Special Circumstances

### 7.1 Litigation Hold

**Definition:** Suspension of normal deletion procedures when litigation is reasonably anticipated.

**Triggers:**
- Receipt of lawsuit or subpoena
- Government investigation
- Internal investigation
- Reasonable anticipation of litigation

**Process:**
1. **Initiation**
   - Legal Counsel issues litigation hold notice
   - Identifies scope of hold (data types, date ranges, individuals)
   - Notifies Privacy Officer and IT

2. **Implementation**
   - Flag affected records in database (litigation_hold = true)
   - Suspend automated deletion for flagged records
   - Notify custodians of hold
   - Document hold scope and date

3. **Maintenance**
   - Quarterly review of active holds
   - Update scope if needed
   - Ensure hold remains in effect

4. **Termination**
   - Legal Counsel determines hold can be lifted
   - Remove litigation_hold flags
   - Resume normal retention schedule
   - Document hold lift date

**Documentation:**
- Litigation hold notice
- Scope documentation
- Custodian acknowledgments
- Hold lift authorization

### 7.2 Patient Requests (Right to Erasure)

**HIPAA:** No explicit "right to erasure" (unlike GDPR), but patients can request amendment or restriction.

**DentaFlow Policy:** Honor patient deletion requests where legally permissible.

**Exceptions (Cannot Delete):**
- Records required by law (e.g., state retention requirements)
- Records needed for ongoing treatment
- Records subject to litigation hold
- Records needed for regulatory compliance

**Process:**
1. **Request Receipt**
   - Patient submits deletion request
   - Verify patient identity
   - Document request

2. **Legal Review**
   - Privacy Officer reviews request
   - Determines if deletion is permissible
   - Identifies any legal barriers

3. **Response**
   - If permissible: Execute deletion per manual process
   - If not permissible: Explain reason to patient, offer alternatives (amendment, restriction)

4. **Documentation**
   - Log request and response
   - Maintain record of decision
   - If deleted: Generate deletion certificate

**Timeline:** 30 days from request

### 7.3 Data Breach

**Impact on Retention:**
- Affected data may need to be retained longer for investigation
- Incident response documentation must be retained for 6 years
- Breach notification records must be retained for 6 years

**Process:**
1. Place litigation hold on affected data
2. Conduct investigation
3. Retain all incident-related documentation
4. After investigation concludes: Resume normal retention schedule (if no litigation)

### 7.4 Business Closure or Sale

**Scenario 1: Business Closure**
- Transfer patient records to successor provider (if applicable)
- If no successor: Notify patients of record location
- Retain records per state requirements
- Arrange long-term storage with qualified vendor
- Maintain HIPAA compliance during storage

**Scenario 2: Business Sale**
- Transfer patient records to acquiring entity
- Ensure Business Associate Agreement (BAA) in place
- Notify patients of transfer
- Acquiring entity assumes retention obligations
- Document transfer in audit log

---

## 8. Backup and Disaster Recovery

### 8.1 Backup Retention

**Automated Backups (Cloud SQL):**
- **Retention:** 30 days
- **Frequency:** Daily
- **Location:** Multi-region (us)

**Point-in-Time Recovery:**
- **Retention:** 7 days
- **Granularity:** Second-level recovery

**Manual Backups:**
- **Retention:** 90 days
- **Frequency:** On-demand
- **Location:** GCS (Nearline storage)

**Backup Deletion:**
- Backups older than retention period are automatically deleted
- Exception: Backups under litigation hold are preserved

### 8.2 Data in Backups

**Challenge:** Backups may contain data that should be deleted per retention policy.

**DentaFlow Approach:**
1. **Primary Deletion:** Delete from primary database immediately
2. **Backup Deletion:** Delete from backups >30 days old during monthly deletion job
3. **Recent Backups:** Data may persist in backups <30 days (acceptable for operational continuity)
4. **Cryptographic Erasure:** Deletion of encryption keys renders data in backups unrecoverable

**Justification:**
- Balances data retention compliance with disaster recovery needs
- Cryptographic erasure provides functional deletion even if data persists in backups
- 30-day backup retention is industry standard for operational recovery

---

## 9. Implementation & Technical Controls

### 9.1 Database Schema

**Retention Metadata:**
```sql
-- Add retention metadata to all tables containing PHI
ALTER TABLE patients ADD COLUMN retention_date DATE;
ALTER TABLE patients ADD COLUMN litigation_hold BOOLEAN DEFAULT FALSE;
ALTER TABLE patients ADD COLUMN deletion_scheduled BOOLEAN DEFAULT FALSE;

-- Automatically calculate retention_date on insert/update
CREATE TRIGGER set_retention_date
BEFORE INSERT OR UPDATE ON patients
FOR EACH ROW
EXECUTE FUNCTION calculate_retention_date();

-- Function to calculate retention date (10 years from last encounter)
CREATE FUNCTION calculate_retention_date() RETURNS TRIGGER AS $$
BEGIN
    NEW.retention_date := (SELECT MAX(appointment_date) FROM appointments WHERE patient_id = NEW.id) + INTERVAL '10 years';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 9.2 Automated Deletion Job

**Implementation:** Cloud Scheduler + Cloud Run Job

**Schedule:** First Sunday of each month at 2:00 AM UTC

**Job Logic:**
```python
import logging
from datetime import datetime, timedelta
from google.cloud import sql, storage
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def monthly_deletion_job(request):
    """
    Monthly automated deletion job for expired records.
    """
    logger = logging.getLogger(__name__)
    
    # 1. Identify expired records
    expired_records = identify_expired_records()
    logger.info(f"Found {len(expired_records)} expired records")
    
    # 2. Exclude litigation holds
    eligible_records = [r for r in expired_records if not r.litigation_hold]
    logger.info(f"{len(eligible_records)} eligible for deletion")
    
    # 3. Send review notification
    send_review_notification(eligible_records)
    
    # 4. Wait 48 hours for approval (job will be re-invoked)
    if not is_review_period_complete():
        return {"status": "pending_review", "count": len(eligible_records)}
    
    # 5. Get approved deletions
    approved = get_approved_deletions()
    logger.info(f"{len(approved)} approved for deletion")
    
    # 6. Execute deletions
    deleted_count = 0
    for record in approved:
        try:
            delete_record(record)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to delete record {record.id}: {e}")
    
    # 7. Generate report
    generate_deletion_report(deleted_count, len(approved))
    
    # 8. Notify completion
    notify_completion(deleted_count)
    
    return {"status": "complete", "deleted": deleted_count}

def identify_expired_records():
    """Query database for records past retention period."""
    query = """
        SELECT * FROM patients
        WHERE retention_date < CURRENT_DATE
        AND deletion_scheduled = FALSE
    """
    # Execute query and return results
    pass

def delete_record(record):
    """Securely delete a single record."""
    # 1. Delete from primary database
    db.execute("DELETE FROM patients WHERE id = ?", record.id)
    
    # 2. Delete encryption keys (cryptographic erasure)
    kms.delete_key(record.encryption_key_id)
    
    # 3. Delete from search indexes
    search.delete_document(record.id)
    
    # 4. Delete from caches
    cache.delete(f"patient:{record.id}")
    
    # 5. Log deletion
    audit_log.log_deletion(record.id, datetime.now())
    
    logger.info(f"Deleted record {record.id}")
```

### 9.3 Monitoring & Alerts

**Metrics:**
- Records pending deletion
- Records deleted (monthly)
- Deletion job success/failure
- Retention policy violations

**Alerts:**
- Deletion job failure
- Records past retention period (not deleted)
- Litigation hold records approaching retention expiration

**Dashboard:**
- Real-time retention metrics
- Deletion history
- Litigation hold status
- Compliance score

---

## 10. Roles & Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Privacy Officer** | Policy owner, approve deletions, litigation hold management, patient requests |
| **Security Lead** | Technical implementation, deletion job monitoring, audit log review |
| **Legal Counsel** | Legal guidance, litigation hold decisions, regulatory compliance |
| **Database Administrator** | Database maintenance, backup management, deletion execution |
| **DevOps Team** | Automation, monitoring, infrastructure |
| **Compliance Team** | Policy review, audit support, training |

---

## 11. Training & Awareness

**All Staff:**
- Annual training on data retention policy
- Understanding of retention periods
- How to request manual deletion
- Litigation hold procedures

**IT Staff:**
- Technical implementation details
- Deletion procedures
- Backup management
- Troubleshooting

**Privacy Officer:**
- Advanced training on HIPAA retention requirements
- State law variations
- Litigation hold management
- Patient request handling

---

## 12. Audit & Compliance

### 12.1 Internal Audits

**Frequency:** Quarterly

**Scope:**
- Review deletion logs
- Verify retention periods are enforced
- Check for records past retention period
- Assess litigation hold compliance
- Review patient deletion requests

**Deliverables:**
- Audit report
- Findings and recommendations
- Corrective action plan (if needed)

### 12.2 External Audits

**Frequency:** Annually (or as required by regulators)

**Scope:**
- HIPAA compliance assessment
- State law compliance
- Data retention policy review
- Deletion procedure verification

**Deliverables:**
- Audit report
- Certification (if applicable)
- Remediation plan (if needed)

### 12.3 Metrics & Reporting

**Monthly Metrics:**
- Records deleted
- Records pending deletion
- Deletion job success rate
- Average retention period

**Quarterly Reports:**
- Retention compliance score
- Litigation hold summary
- Patient request summary
- Policy violations (if any)

**Annual Report:**
- Comprehensive retention review
- Policy effectiveness assessment
- Recommendations for improvements

---

## 13. Policy Review & Updates

**Review Frequency:** Annually (or when triggered by regulatory changes)

**Review Triggers:**
- Regulatory changes (HIPAA, state laws)
- Business changes (new services, new states)
- Audit findings
- Security incidents
- Technology changes

**Review Process:**
1. Privacy Officer initiates review
2. Gather feedback from stakeholders
3. Research regulatory updates
4. Draft policy updates
5. Legal review
6. Executive approval
7. Communicate changes
8. Update technical implementation
9. Train staff

**Approval:** Privacy Officer, Legal Counsel, Executive Leadership

---

## 14. Exceptions

**Exception Process:**
1. Request submitted to Privacy Officer
2. Justification documented
3. Legal review (if needed)
4. Privacy Officer approval
5. Exception logged
6. Periodic review of active exceptions

**Example Exceptions:**
- Extended retention for research purposes (with patient consent)
- Early deletion for patient safety (e.g., incorrect data)
- Retention beyond standard period for quality improvement

---

## 15. Related Policies

- HIPAA Privacy Policy
- HIPAA Security Policy
- Incident Response Plan
- Backup and Disaster Recovery Policy
- Business Associate Agreement (BAA) Template

---

## 16. Contact Information

**Questions about this policy:**
- Privacy Officer: privacy@dentaflow.ai
- Legal Counsel: legal@dentaflow.ai
- Security Lead: security@dentaflow.ai

**To request deletion:**
- Patient Portal: Submit request via "My Data" page
- Email: privacy@dentaflow.ai
- Phone: [To be configured]

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Oct 19, 2025 | Manus AI | Initial version |

**Next Review Date:** October 19, 2026

**Approval:**
- Privacy Officer: ___ Date: ___
- Legal Counsel: ___ Date: ___
- Executive Leadership: ___ Date: ___

---

**END OF DOCUMENT**

