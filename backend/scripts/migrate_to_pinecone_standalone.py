"""
Migrate all knowledge bases to Pinecone - Standalone Version

This script migrates clinical, financial, operational, and general knowledge
to Pinecone without requiring full app configuration.
"""

import os
import logging
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Knowledge base content
CLINICAL_KNOWLEDGE = [
    {
        'id': 'dental_procedures_overview',
        'title': 'Common Dental Procedures',
        'content': """
# Common Dental Procedures

## Preventive Procedures
- Professional Cleaning (Prophylaxis): Every 6 months
- Fluoride Treatment: Strengthens enamel
- Dental Sealants: Prevents cavities in molars

## Restorative Procedures
- Fillings: Treats cavities with amalgam or composite
- Crowns: Covers damaged teeth, lasts 10-15 years
- Root Canal: Treats infected tooth pulp

## Cosmetic Procedures
- Teeth Whitening: 2-8 shades lighter
- Veneers: Porcelain or composite, lasts 10-15 years

## Surgical Procedures
- Tooth Extraction: Simple or surgical
- Dental Implants: 95-98% success rate, lasts 20+ years
        """,
        'category': 'procedures'
    },
    {
        'id': 'dental_drug_interactions',
        'title': 'Common Dental Drug Interactions',
        'content': """
# Dental Drug Interactions

## Local Anesthetics
- Lidocaine: Max 4.4 mg/kg with epinephrine
- Interactions with beta-blockers and antiarrhythmics

## Antibiotics
- Amoxicillin 500mg TID for 7-10 days
- May reduce oral contraceptive effectiveness
- Increases warfarin bleeding risk

## Pain Management
- NSAIDs: Max ibuprofen 2400mg/day
- Acetaminophen: Max 4000mg/day
- Opioids: Use with caution, addiction potential

## Anticoagulated Patients
- Warfarin: Check INR, most procedures safe if INR <4
- NOACs: Consider skipping morning dose
- Continue aspirin/clopidogrel for dental procedures
        """,
        'category': 'pharmacology'
    }
]

FINANCIAL_KNOWLEDGE = [
    {
        'id': 'israeli_tax_overview',
        'title': 'Israeli Tax System for Dental Clinics',
        'content': """
# Israeli Tax System for Dental Clinics (2024-2025)

## Income Tax Brackets
- Up to ₪81,480: 10%
- ₪81,481 - ₪116,880: 14%
- ₪116,881 - ₪187,440: 20%
- ₪187,441 - ₪260,880: 31%
- ₪260,881 - ₪544,320: 35%
- ₪544,321 - ₪721,560: 47%
- Above ₪721,560: 50%

## VAT (Value Added Tax)
- Standard rate: 17%
- Most dental services: TAXABLE
- Registration threshold: ₪102,292 annual revenue
- Monthly or bi-monthly returns required

## Deductible Expenses
- Equipment and supplies
- Rent and utilities
- Salaries and benefits
- Professional insurance
- Continuing education
- Marketing and advertising

## Tax Planning
- Quarterly advance payments required
- Annual tax return deadline: May 31
- Keep detailed records for 7 years
- Consult certified accountant (רו"ח) for complex situations
        """,
        'category': 'tax'
    }
]

OPERATIONAL_KNOWLEDGE = [
    {
        'id': 'safety_protocols',
        'title': 'Dental Clinic Safety Protocols',
        'content': """
# Dental Clinic Safety Protocols

## Infection Control
- Hand hygiene: Before and after each patient
- Personal protective equipment (PPE): Gloves, masks, eye protection
- Sterilization: Autoclave all instruments, 121°C for 15 minutes
- Surface disinfection: EPA-registered disinfectants

## Emergency Preparedness
- Emergency kit: Check monthly, replace expired items
- CPR training: All staff certified, renew every 2 years
- Emergency protocols: Posted and practiced quarterly
- Emergency contacts: Displayed prominently

## Equipment Maintenance
- Autoclave: Biological testing weekly
- X-ray equipment: Annual inspection required
- Dental chairs: Monthly maintenance check
- Suction systems: Daily cleaning and weekly disinfection

## Compliance
- Israeli Ministry of Health regulations
- Occupational safety standards
- Waste disposal: Separate medical and regular waste
- Documentation: Maintain records for 7 years
        """,
        'category': 'safety'
    }
]

GENERAL_KNOWLEDGE = [
    {
        'id': 'clinic_policies',
        'title': 'Dental Clinic Policies',
        'content': """
# Dental Clinic Policies

## Appointment Policy
- Booking: Online, phone, or in-person
- Cancellation: 24 hours notice required
- Late arrival: May need to reschedule if >15 minutes late
- No-show: May charge cancellation fee

## Payment Policy
- Payment due at time of service
- Accepted: Cash, credit card, bank transfer
- Insurance: Direct billing available for some providers
- Payment plans: Available for treatments over ₪5,000

## Privacy Policy
- Patient information: Confidential and secure
- Medical records: Maintained for 7 years
- Data protection: Compliant with Israeli privacy laws
- Patient rights: Access, correction, and deletion of data

## Office Hours
- Sunday to Thursday: 8:00 AM - 7:00 PM
- Friday: 8:00 AM - 2:00 PM
- Saturday: Closed
- Emergency contact: Available 24/7
        """,
        'category': 'policies'
    }
]


def migrate_knowledge_to_pinecone():
    """Migrate all knowledge bases to Pinecone."""
    
    logger.info("="*60)
    logger.info("MIGRATION: Knowledge → Pinecone")
    logger.info("="*60)
    
    # Get API keys
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not pinecone_api_key:
        logger.error("PINECONE_API_KEY not set")
        return False
    
    if not openai_api_key:
        logger.error("OPENAI_API_KEY not set")
        return False
    
    # Initialize clients
    logger.info("Initializing Pinecone and OpenAI...")
    pc = Pinecone(api_key=pinecone_api_key)
    
    # Initialize OpenAI with direct API (not through Manus proxy)
    openai_client = OpenAI(
        api_key=openai_api_key,
        base_url="https://api.openai.com/v1"  # Direct OpenAI API
    )
    
    # Index name
    index_name = "dentaflow-knowledge"
    
    # Check if index exists, create if not
    existing_indexes = pc.list_indexes()
    index_names = [idx['name'] for idx in existing_indexes]
    
    if index_name not in index_names:
        logger.info(f"Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        logger.info("Index created successfully")
    else:
        logger.info(f"Index already exists: {index_name}")
    
    # Get index
    index = pc.Index(index_name)
    
    # Knowledge bases to migrate
    knowledge_bases = {
        'clinical': CLINICAL_KNOWLEDGE,
        'financial': FINANCIAL_KNOWLEDGE,
        'operational': OPERATIONAL_KNOWLEDGE,
        'general': GENERAL_KNOWLEDGE,
    }
    
    total_uploaded = 0
    total_failed = 0
    
    # Upload each knowledge base
    for domain, documents in knowledge_bases.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Uploading {domain.upper()} knowledge...")
        logger.info(f"{'='*60}")
        
        for doc in documents:
            try:
                # Generate embedding
                logger.info(f"  Processing: {doc['title']}")
                response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=doc['content']
                )
                embedding = response.data[0].embedding
                
                # Prepare metadata
                metadata = {
                    'title': doc['title'],
                    'category': doc.get('category', 'general'),
                    'domain': domain,
                    'text': doc['content'][:5000],  # First 5000 chars
                }
                
                # Upsert to Pinecone
                index.upsert(
                    vectors=[{
                        'id': f"{domain}_{doc['id']}",
                        'values': embedding,
                        'metadata': metadata
                    }],
                    namespace=domain
                )
                
                logger.info(f"    ✅ Uploaded: {doc['id']}")
                total_uploaded += 1
                
            except Exception as e:
                logger.error(f"    ❌ Failed: {doc['id']} - {e}")
                total_failed += 1
    
    # Get stats
    logger.info(f"\n{'='*60}")
    logger.info("PINECONE INDEX STATS")
    logger.info(f"{'='*60}")
    
    stats = index.describe_index_stats()
    for namespace, ns_stats in stats.namespaces.items():
        logger.info(f"  {namespace:15s}: {ns_stats.vector_count:5d} vectors")
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("MIGRATION SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Uploaded: {total_uploaded}")
    logger.info(f"❌ Failed: {total_failed}")
    logger.info(f"{'='*60}")
    
    return total_failed == 0


if __name__ == "__main__":
    import sys
    success = migrate_knowledge_to_pinecone()
    sys.exit(0 if success else 1)

