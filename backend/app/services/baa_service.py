"""
Business Associate Agreement (BAA) service.

Handles BAA document generation, signature, and PDF creation.
"""

import hashlib
from datetime import datetime
from typing import Optional


class BAAService:
    """Service for managing BAA documents and signatures."""
    
    @staticmethod
    def get_baa_text(version: str = "1.0") -> str:
        """
        Get the BAA agreement text.
        
        Args:
            version: BAA version (default: "1.0")
            
        Returns:
            Full BAA text in Hebrew and English
        """
        # This is a simplified version. In production, load from a template file.
        return """
# BUSINESS ASSOCIATE AGREEMENT (BAA)
# הסכם שותף עסקי

**Version:** {version}  
**Effective Date:** {date}

---

## 1. DEFINITIONS / הגדרות

**"Covered Entity"** means the healthcare provider (dental clinic) using DentaFlow services.

**"Business Associate"** means DentaFlow Ltd., providing SaaS dental management services.

**"Protected Health Information (PHI)"** means individually identifiable health information as defined by HIPAA.

---

## 2. OBLIGATIONS OF BUSINESS ASSOCIATE / התחייבויות השותף העסקי

### 2.1 Permitted Uses and Disclosures / שימושים וחשיפות מותרות

Business Associate shall:
- Use or disclose PHI only as permitted by this Agreement or as required by law
- Use appropriate safeguards to prevent unauthorized use or disclosure of PHI
- Implement administrative, physical, and technical safeguards per HIPAA Security Rule

השותף העסקי מתחייב:
- להשתמש או לחשוף מידע רפואי מוגן רק כפי שמותר בהסכם זה או כנדרש בחוק
- להשתמש באמצעי הגנה מתאימים למניעת שימוש או חשיפה לא מורשים
- ליישם אמצעי הגנה מנהליים, פיזיים וטכניים לפי כללי האבטחה של HIPAA

### 2.2 Safeguards / אמצעי הגנה

Business Associate shall implement:
- **Encryption:** All PHI encrypted at rest (AES-256) and in transit (TLS 1.3)
- **Access Control:** Role-based access control (RBAC) with unique user IDs
- **Audit Logs:** Comprehensive logging of all PHI access
- **Backup & Recovery:** Regular backups with tested recovery procedures
- **Incident Response:** Documented breach notification procedures

השותף העסקי מיישם:
- **הצפנה:** כל המידע הרפואי מוצפן במנוחה (AES-256) ובתנועה (TLS 1.3)
- **בקרת גישה:** בקרת גישה מבוססת תפקידים עם מזהים ייחודיים
- **יומני ביקורת:** תיעוד מקיף של כל גישה למידע רפואי
- **גיבוי ושחזור:** גיבויים קבועים עם נהלי שחזור נבדקים
- **תגובה לאירועים:** נהלים מתועדים להודעה על הפרות

### 2.3 Reporting / דיווח

Business Associate shall report to Covered Entity:
- Any unauthorized use or disclosure of PHI within 24 hours
- Any security incident within 72 hours
- Annual security assessment results

השותף העסקי ידווח לישות המכוסה:
- כל שימוש או חשיפה לא מורשים של מידע רפואי תוך 24 שעות
- כל אירוע אבטחה תוך 72 שעות
- תוצאות הערכת אבטחה שנתית

---

## 3. OBLIGATIONS OF COVERED ENTITY / התחייבויות הישות המכוסה

Covered Entity shall:
- Provide Business Associate with necessary permissions to perform services
- Inform Business Associate of any changes to PHI use or disclosure permissions
- Not request Business Associate to use or disclose PHI in violation of HIPAA

הישות המכוסה מתחייבת:
- לספק לשותף העסקי הרשאות נדרשות לביצוע השירותים
- להודיע לשותף העסקי על כל שינוי בהרשאות שימוש או חשיפה
- לא לבקש מהשותף העסקי להשתמש או לחשוף מידע בניגוד ל-HIPAA

---

## 4. TERM AND TERMINATION / תקופה וסיום

### 4.1 Term / תקופה

This Agreement is effective as of the date signed and shall continue until terminated.

הסכם זה תקף מתאריך החתימה ויימשך עד לסיומו.

### 4.2 Termination / סיום

Either party may terminate this Agreement:
- With 30 days written notice
- Immediately if the other party breaches a material term

כל צד רשאי לסיים הסכם זה:
- בהודעה בכתב של 30 יום
- מיידית אם הצד השני מפר תנאי מהותי

### 4.3 Return or Destruction of PHI / החזרה או השמדת מידע

Upon termination, Business Associate shall:
- Return or destroy all PHI within 30 days
- Provide written certification of destruction
- Retain PHI only as required by law

עם הסיום, השותף העסקי:
- יחזיר או ישמיד את כל המידע הרפואי תוך 30 יום
- יספק אישור בכתב על ההשמדה
- ישמור מידע רפואי רק כנדרש בחוק

---

## 5. MISCELLANEOUS / שונות

### 5.1 Governing Law / דין חל

This Agreement shall be governed by Israeli law and HIPAA regulations.

הסכם זה יהיה כפוף לדין הישראלי ולתקנות HIPAA.

### 5.2 Amendment / תיקון

This Agreement may be amended only by written agreement of both parties.

ניתן לתקן הסכם זה רק בהסכמה בכתב של שני הצדדים.

---

## 6. SIGNATURES / חתימות

By signing below, both parties acknowledge that they have read, understood, and agree to be bound by the terms of this Business Associate Agreement.

בחתימה למטה, שני הצדדים מאשרים שקראו, הבינו, ומסכימים להיות כפופים לתנאי הסכם שותף עסקי זה.

---

**DentaFlow Ltd.**  
Business Associate / שותף עסקי

**Covered Entity:**  
[Organization Name]  
[Signatory Name]  
[Signatory Title]  
[Date]

---

**Contact Information:**  
DentaFlow Ltd.  
Email: legal@dentaflow.co.il  
Phone: +972-XX-XXX-XXXX

---

*This is a legally binding agreement. Please consult with legal counsel before signing.*  
*זהו הסכם משפטי מחייב. אנא התייעץ עם יועץ משפטי לפני החתימה.*
        """.format(version=version, date=datetime.now().strftime("%B %d, %Y"))
    
    @staticmethod
    def calculate_content_hash(baa_text: str) -> str:
        """
        Calculate SHA-256 hash of BAA content.
        
        Args:
            baa_text: Full BAA text
            
        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(baa_text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_consent_text() -> str:
        """
        Generate consent checkbox text.
        
        Returns:
            Consent text in Hebrew and English
        """
        return """
אני מאשר/ת שקראתי והבנתי את הסכם השותף העסקי (BAA) ומסכים/ה לתנאיו.

I confirm that I have read and understood the Business Associate Agreement (BAA) and agree to its terms.
        """.strip()


# Singleton instance
baa_service = BAAService()
