"""
Knowledge Base Manager

Manages clinical, financial, and operational knowledge for RAG.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from app.services.vector_db import vector_db

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """
    Manages knowledge bases for different domains.
    
    Domains:
    - Clinical: Treatment guidelines, procedures, drug interactions
    - Financial: Tax laws, accounting best practices, Israeli regulations
    - Operational: Best practices, compliance, safety protocols
    - General: Clinic policies, FAQs, common procedures
    """
    
    def __init__(self):
        """Initialize knowledge base manager."""
        self.vector_db = vector_db
        self.knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self.knowledge_dir.mkdir(exist_ok=True)
    
    def ingest_document(
        self,
        domain: str,
        doc_id: str,
        title: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Ingest a document into the knowledge base.
        
        Args:
            domain: Knowledge domain ('clinical', 'financial', 'operational', 'general')
            doc_id: Unique document ID
            title: Document title
            content: Document content
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        try:
            # Prepare metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                'title': title,
                'domain': domain,
                'ingested_at': datetime.now().isoformat(),
                'content_length': len(content),
            })
            
            # Upsert to vector DB
            success = self.vector_db.upsert_document(
                index_type=domain,
                doc_id=doc_id,
                text=content,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Ingested document: {title} ({domain})")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to ingest document: {e}")
            return False
    
    def ingest_clinical_knowledge(self):
        """Ingest clinical knowledge base."""
        logger.info("Ingesting clinical knowledge...")
        
        # Dental procedures
        self.ingest_document(
            domain='clinical',
            doc_id='dental_procedures_overview',
            title='Common Dental Procedures',
            content="""
# Common Dental Procedures

## Preventive Procedures

### Professional Cleaning (Prophylaxis)
- Frequency: Every 6 months for healthy patients
- Duration: 30-60 minutes
- Purpose: Remove plaque and tartar, prevent gum disease
- Cost range: 200-400 ILS

### Fluoride Treatment
- Recommended for: Children, high cavity risk patients
- Application: Gel, foam, or varnish
- Duration: 1-4 minutes
- Benefits: Strengthens enamel, prevents decay

### Dental Sealants
- Target: Molars and premolars
- Best age: 6-14 years
- Duration: Lasts 5-10 years
- Purpose: Prevent cavities in deep grooves

## Restorative Procedures

### Fillings (Amalgam/Composite)
- Indications: Cavities, tooth decay
- Materials: Amalgam (silver) or composite (tooth-colored)
- Duration: 30-60 minutes per tooth
- Anesthesia: Local anesthetic usually required

### Crowns
- Indications: Large cavities, broken teeth, root canal teeth
- Materials: Porcelain, metal, or porcelain-fused-to-metal
- Process: 2 visits (preparation + placement)
- Lifespan: 10-15 years with proper care

### Root Canal Treatment
- Indications: Infected or damaged tooth pulp
- Steps: Remove pulp, clean canal, seal tooth
- Duration: 1-2 hours (may require multiple visits)
- Success rate: 85-97%

## Cosmetic Procedures

### Teeth Whitening
- Methods: In-office or take-home kits
- Duration: 30-90 minutes (in-office)
- Results: 2-8 shades lighter
- Maintenance: Touch-ups every 6-12 months

### Veneers
- Purpose: Improve appearance of teeth
- Material: Porcelain or composite resin
- Process: 2-3 visits
- Lifespan: 10-15 years (porcelain), 5-7 years (composite)

## Surgical Procedures

### Tooth Extraction
- Indications: Severe decay, infection, crowding
- Types: Simple or surgical
- Healing time: 1-2 weeks
- Follow-up: Consider replacement options

### Dental Implants
- Purpose: Replace missing teeth
- Process: 3-6 months (osseointegration)
- Success rate: 95-98%
- Lifespan: 20+ years with proper care

## Orthodontic Procedures

### Braces
- Duration: 18-36 months average
- Types: Metal, ceramic, lingual
- Adjustments: Every 4-8 weeks
- Retention: Permanent or removable retainers

### Clear Aligners (Invisalign)
- Duration: 12-18 months average
- Advantages: Removable, nearly invisible
- Compliance: Must wear 20-22 hours/day
- Cost: Generally higher than traditional braces
            """,
            metadata={'category': 'procedures', 'language': 'en'}
        )
        
        # Drug interactions
        self.ingest_document(
            domain='clinical',
            doc_id='dental_drug_interactions',
            title='Common Dental Drug Interactions',
            content="""
# Dental Drug Interactions

## Local Anesthetics

### Lidocaine
- Common interactions:
  - Beta-blockers: May prolong anesthetic effect
  - Antiarrhythmics: Risk of cardiac toxicity
  - MAO inhibitors: Avoid epinephrine-containing solutions
- Maximum dose: 4.4 mg/kg (with epinephrine), 3.2 mg/kg (without)

### Articaine
- Interactions similar to lidocaine
- Advantage: Better tissue penetration
- Caution: Higher risk of paresthesia in mandibular blocks

## Antibiotics

### Amoxicillin
- Interactions:
  - Oral contraceptives: May reduce effectiveness
  - Warfarin: Increases bleeding risk
  - Methotrexate: Increases toxicity risk
- Dosage: 500mg TID for 7-10 days

### Metronidazole
- Serious interactions:
  - Alcohol: Disulfiram-like reaction (avoid for 48h after)
  - Warfarin: Significantly increases INR
  - Lithium: Risk of toxicity
- Dosage: 500mg TID for 7 days

### Clindamycin
- Use: Alternative for penicillin-allergic patients
- Interactions:
  - Neuromuscular blockers: Enhanced effect
  - Erythromycin: Antagonistic effect
- Risk: C. difficile colitis (rare but serious)

## Pain Management

### NSAIDs (Ibuprofen, Naproxen)
- Interactions:
  - Aspirin: Reduced cardioprotective effect
  - Warfarin/NOACs: Increased bleeding risk
  - ACE inhibitors: Reduced antihypertensive effect
  - Lithium: Increased levels
- Maximum ibuprofen: 2400mg/day

### Acetaminophen (Paracetamol)
- Safer interaction profile than NSAIDs
- Interactions:
  - Warfarin: May increase INR at high doses
  - Alcohol: Hepatotoxicity risk
- Maximum dose: 4000mg/day (3000mg in elderly)

### Opioids (Codeine, Tramadol)
- Interactions:
  - SSRIs/SNRIs: Serotonin syndrome risk (especially tramadol)
  - Benzodiazepines: Respiratory depression
  - CYP2D6 inhibitors: Reduced codeine efficacy
- Caution: Addiction potential, respiratory depression

## Considerations for Anticoagulated Patients

### Warfarin
- INR target: Usually 2-3
- Dental procedures:
  - INR <4: Most procedures safe
  - INR >4: Consult physician
- Do NOT stop warfarin for routine extractions

### NOACs (Apixaban, Rivaroxaban, Dabigatran)
- Lower bleeding risk than warfarin
- Consider skipping morning dose on day of surgery
- Restart same day after hemostasis achieved

### Antiplatelet Agents (Aspirin, Clopidogrel)
- Generally continue for dental procedures
- Increased bleeding risk but manageable
- Use local hemostatic measures

## Special Populations

### Pregnancy
- Safe: Lidocaine, penicillins, acetaminophen
- Avoid: NSAIDs (3rd trimester), tetracyclines, metronidazole (1st trimester)
- Best timing: 2nd trimester

### Pediatrics
- Dose by weight
- Avoid: Tetracyclines (<8 years), aspirin (Reye's syndrome)
- Fluoride supplementation based on water fluoridation

### Elderly
- Start low, go slow
- Increased sensitivity to CNS effects
- Polypharmacy concerns
- Reduced renal/hepatic function
            """,
            metadata={'category': 'pharmacology', 'language': 'en', 'critical': True}
        )
        
        logger.info("Clinical knowledge ingestion complete")
    
    def ingest_financial_knowledge(self):
        """Ingest financial and tax knowledge."""
        logger.info("Ingesting financial knowledge...")
        
        # Already exists in israeli_tax_laws.py, but add to vector DB
        self.ingest_document(
            domain='financial',
            doc_id='israeli_tax_overview',
            title='Israeli Tax System for Dental Clinics',
            content="""
# Israeli Tax System for Dental Clinics

## Income Tax

### Tax Brackets (2024)
- Up to ₪81,480: 10%
- ₪81,481 - ₪116,880: 14%
- ₪116,881 - ₪187,440: 20%
- ₪187,441 - ₪260,880: 31%
- ₪260,881 - ₪544,320: 35%
- ₪544,321 - ₪721,560: 47%
- Above ₪721,560: 50%

### Self-Employed Dentists
- Must file annual tax return
- Quarterly advance payments required
- Deductible expenses: Equipment, supplies, rent, salaries, insurance
- Home office deduction: Proportional to business use

## VAT (Value Added Tax)

### Standard Rate: 17%
- Applied to most dental services
- Exempt services: None (dental services are taxable)
- Registration threshold: ₪102,292 annual revenue

### VAT Reporting
- Monthly or bi-monthly returns
- Input VAT: Deductible on business purchases
- Output VAT: Collected from patients
- Net VAT: Output - Input (paid to tax authority)

## Business Tax (Mas Esek)

### Rates by Municipality
- Tel Aviv: 192% of annual rental value
- Jerusalem: 178%
- Haifa: 184%
- Varies by location

### Exemptions
- First 2 years for new businesses (conditions apply)
- Home-based businesses (under certain conditions)

## National Insurance (Bituach Leumi)

### Self-Employed Rates (2024)
- Up to average wage: 17.83%
- Above average wage: 12.95%
- Minimum payment even with low income
- Provides: Pension, disability, maternity benefits

## Payroll Taxes (for Employees)

### Employer Obligations
- Income tax withholding
- National Insurance: ~7.6% (employer portion)
- Pension contributions: Minimum 6.5% (employer) + 6% (employee)
- Severance pay fund (Keren Hishtalmut): 7.5% (employer) + 2.5% (employee)

## Deductible Expenses

### Fully Deductible
- Dental supplies and materials
- Equipment purchases (depreciation schedule)
- Professional insurance
- Continuing education
- Professional memberships
- Marketing and advertising
- Office rent and utilities
- Employee salaries and benefits

### Partially Deductible
- Vehicle expenses: Business use percentage
- Mobile phone: Business use percentage
- Home office: Proportional to space used

### Non-Deductible
- Personal expenses
- Fines and penalties
- Excessive entertainment expenses

## Tax Planning Strategies

### Incorporation
- Consider Ltd. company (Chev ra Be'am) if income >₪500,000
- Corporate tax rate: 23% (lower than top personal rates)
- Dividend tax: 25-30% (total effective rate may be higher)

### Pension Contributions
- Tax-deductible up to certain limits
- Reduces taxable income
- Long-term savings benefit

### Equipment Purchases
- Timing: Consider year-end purchases for deductions
- Depreciation: Spread over useful life
- Section 3(i) deduction: Accelerated depreciation for certain assets

## Record Keeping

### Required Documents
- Invoices (must include VAT details)
- Receipts for all expenses
- Bank statements
- Payroll records
- Patient records (for audit trail)

### Retention Period
- 7 years minimum
- Digital records acceptable (with proper backup)

## Common Mistakes to Avoid

1. Mixing personal and business expenses
2. Not keeping proper documentation
3. Missing quarterly advance tax payments
4. Incorrect VAT calculations
5. Not claiming all eligible deductions
6. Late filing of returns (penalties apply)

## When to Consult an Accountant

- Annual tax return preparation
- Business structure decisions
- Major equipment purchases
- Hiring employees
- Tax audit situations
- Complex transactions

**Note:** Tax laws change frequently. Always consult with a certified Israeli accountant for current regulations and personalized advice.
            """,
            metadata={'category': 'tax', 'language': 'en', 'country': 'Israel', 'year': 2024}
        )
        
        logger.info("Financial knowledge ingestion complete")
    
    def ingest_operational_knowledge(self):
        """Ingest operational best practices."""
        logger.info("Ingesting operational knowledge...")
        
        self.ingest_document(
            domain='operational',
            doc_id='clinic_safety_protocols',
            title='Dental Clinic Safety and Compliance Protocols',
            content="""
# Dental Clinic Safety and Compliance Protocols

## Infection Control

### Standard Precautions
- Hand hygiene: Before and after every patient
- Personal protective equipment (PPE):
  - Gloves: Single-use, change between patients
  - Masks: Surgical or N95 for aerosol procedures
  - Eye protection: Goggles or face shields
  - Gowns: Fluid-resistant for surgical procedures

### Sterilization Protocols
- Autoclave: 121°C for 20 minutes or 134°C for 3 minutes
- Biological indicators: Weekly testing
- Chemical indicators: Every load
- Instrument processing:
  1. Pre-cleaning (remove gross debris)
  2. Cleaning (ultrasonic or manual)
  3. Packaging
  4. Sterilization
  5. Storage in sealed packages

### Environmental Disinfection
- Clinical contact surfaces: Disinfect between patients
- Housekeeping surfaces: Daily cleaning
- Dental unit waterlines: Flush and treat regularly
- Suction systems: Clean and disinfect daily

## Radiation Safety

### X-Ray Safety Protocols
- ALARA principle: As Low As Reasonably Achievable
- Lead aprons: Use for all patients
- Thyroid collars: Especially for children and pregnant women
- Proper positioning: Minimize retakes
- Digital radiography: Reduces radiation exposure by 80%

### Regulatory Compliance
- Annual equipment calibration
- Radiation safety officer designation
- Staff training and certification
- Exposure monitoring (for staff)
- Proper signage and warnings

## Occupational Safety

### Ergonomics
- Proper chair and patient positioning
- Regular breaks and stretching
- Magnification loupes: Reduce neck strain
- Saddle stools: Better posture

### Sharps Safety
- Never recap needles
- Dispose immediately in sharps containers
- Containers: Puncture-resistant, labeled, accessible
- Full containers: Replace at 3/4 full

### Hazardous Materials
- Material Safety Data Sheets (MSDS): Accessible to all staff
- Proper storage: Separate incompatible chemicals
- Spill kits: Available and staff trained
- Waste disposal: Follow local regulations

## Emergency Preparedness

### Medical Emergencies
- Emergency kit: Check monthly, replace expired items
- Essential medications:
  - Epinephrine (anaphylaxis)
  - Aspirin (cardiac events)
  - Glucose (hypoglycemia)
  - Albuterol (asthma)
  - Nitroglycerin (angina)
- Oxygen: E-cylinder minimum, check pressure weekly
- AED (Automated External Defibrillator): Check monthly
- Staff training: CPR and basic life support (annual renewal)

### Fire Safety
- Fire extinguishers: Inspect monthly, service annually
- Evacuation plan: Posted and practiced
- Exit routes: Clear and marked
- Electrical safety: Regular inspections

## Regulatory Compliance

### Israeli Ministry of Health Requirements
- Clinic license: Renewal every 5 years
- Professional licenses: Current for all practitioners
- Infection control protocols: Written and followed
- Equipment maintenance: Documented
- Staff training: Ongoing and documented

### Patient Rights
- Informed consent: Before all procedures
- Privacy (HIPAA equivalent): Secure records
- Right to refuse treatment
- Access to medical records
- Clear fee disclosure

## Quality Assurance

### Clinical Audits
- Infection control: Monthly spot checks
- Radiographs: Quality assessment
- Treatment outcomes: Track and review
- Patient satisfaction: Regular surveys

### Continuing Education
- Minimum hours: 30 per year (varies by license)
- Topics: Clinical skills, safety, ethics
- Documentation: Certificates on file

## Inventory Management

### Stock Control
- Par levels: Establish for all supplies
- Reorder points: Before stock runs out
- Expiration dates: FIFO (First In, First Out)
- Controlled substances: Locked storage, log all use

### Equipment Maintenance
- Preventive maintenance: Per manufacturer schedules
- Service records: Keep all documentation
- Backup equipment: For critical items
- Replacement planning: Budget for equipment lifecycle

## Staff Management

### Training Requirements
- New hire orientation: Safety, infection control, policies
- Annual refreshers: All safety topics
- Competency assessments: Document skills
- Cross-training: Ensure coverage

### Workplace Safety
- Injury reporting: Immediate documentation
- Post-exposure protocols: For bloodborne pathogens
- Workers' compensation: Proper coverage
- Ergonomic assessments: Prevent injuries

## Documentation

### Required Records
- Patient charts: Complete and current
- Consent forms: Signed and dated
- Treatment plans: Detailed and approved
- Radiographs: Properly labeled and stored
- Referrals: Track and follow up

### Retention Periods
- Adult records: 7 years after last visit
- Pediatric records: Until age 21 + 7 years
- Financial records: 7 years
- Employment records: 7 years after termination

## Best Practices

### Patient Communication
- Clear explanations: Use lay terms
- Treatment options: Present alternatives
- Cost estimates: Provide in writing
- Follow-up: Confirm appointments, check on outcomes

### Efficiency
- Scheduling: Optimize for procedure types
- Supplies: Keep organized and accessible
- Workflow: Minimize steps and handoffs
- Technology: Use practice management software

### Continuous Improvement
- Regular team meetings
- Incident reporting and review
- Patient feedback analysis
- Benchmark against standards

**Remember:** Compliance is not optional. These protocols protect patients, staff, and the practice.
            """,
            metadata={'category': 'safety', 'language': 'en', 'critical': True}
        )
        
        logger.info("Operational knowledge ingestion complete")
    
    def search_knowledge(
        self,
        domain: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base for relevant information.
        
        Args:
            domain: Knowledge domain to search
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant documents
        """
        return self.vector_db.search(
            index_type=domain,
            query=query,
            top_k=top_k
        )
    
    def initialize_all_knowledge(self):
        """Initialize all knowledge bases."""
        if not self.vector_db.enabled:
            logger.warning("Vector DB disabled - skipping knowledge ingestion")
            return False
        
        try:
            logger.info("Initializing all knowledge bases...")
            
            self.ingest_clinical_knowledge()
            self.ingest_financial_knowledge()
            self.ingest_operational_knowledge()
            
            logger.info("All knowledge bases initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize knowledge bases: {e}")
            return False


# Global instance
knowledge_base = KnowledgeBaseManager()

