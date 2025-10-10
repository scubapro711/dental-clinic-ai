"""
Tax Calculation Tools for Marcus (CFO Agent)

Tools for calculating Israeli taxes and providing tax advice.

Reference: Phase 3 - Marcus Expansion with Israeli Tax Knowledge
"""

import logging
from typing import Optional
from langchain.tools import tool

from app.agents.knowledge.israeli_tax_laws import (
    calculate_income_tax_individual,
    calculate_income_tax_company,
    calculate_vat,
    ISRAELI_TAX_KNOWLEDGE,
)

logger = logging.getLogger(__name__)


@tool
def calculate_income_tax(
    annual_income: float,
    entity_type: str = "individual"
) -> str:
    """
    Calculate Israeli income tax for the clinic.
    
    Args:
        annual_income: Annual income in ILS
        entity_type: "individual" for self-employed dentist or "company" for Ltd company
        
    Returns:
        Tax calculation breakdown as formatted string
    """
    try:
        if entity_type.lower() == "company":
            result = calculate_income_tax_company(annual_income)
            
            output = f"""
💼 **חישוב מס הכנסה - חברה בע"מ**

📊 **הכנסה שנתית:** ₪{result['annual_income']:,.2f}
📈 **שיעור מס:** {result['tax_rate']}
💰 **מס לתשלום:** ₪{result['total_tax']:,.2f}
✅ **הכנסה נטו:** ₪{result['net_income']:,.2f}

**הערה:** חברות משלמות מס אחיד של 23% על כל ההכנסה.

⚠️ **חשוב:** זהו חישוב כללי בלבד. להחלטות מיסויות ספציפיות, יש להתייעץ עם רו"ח מוסמך.
"""
        else:
            result = calculate_income_tax_individual(annual_income)
            
            output = f"""
👤 **חישוב מס הכנסה - עוסק עצמאי**

📊 **הכנסה שנתית:** ₪{result['annual_income']:,.2f}
💰 **מס לתשלום:** ₪{result['total_tax']:,.2f}
📈 **שיעור מס אפקטיבי:** {result['effective_rate']:.1f}%
✅ **הכנסה נטו:** ₪{result['net_income']:,.2f}

**פירוט לפי מדרגות:**
"""
            for bracket in result['breakdown']:
                if bracket['taxable'] > 0:
                    output += f"\n- {bracket['bracket']}: {bracket['rate']} = ₪{bracket['tax']:,.2f}"
            
            output += "\n\n⚠️ **חשוב:** זהו חישוב כללי בלבד. להחלטות מיסויות ספציפיות, יש להתייעץ עם רו\"ח מוסמך."
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error calculating income tax: {e}")
        return f"שגיאה בחישוב מס הכנסה: {str(e)}"


@tool
def calculate_vat_amount(
    amount: float,
    treatment_type: str = "regular"
) -> str:
    """
    Calculate VAT for dental services.
    
    Args:
        amount: Service amount in ILS
        treatment_type: "regular" (exempt), "aesthetic" (taxable), or "product" (taxable)
        
    Returns:
        VAT calculation as formatted string
    """
    try:
        is_exempt = treatment_type.lower() == "regular"
        result = calculate_vat(amount, is_exempt)
        
        output = f"""
🧾 **חישוב מע"מ**

💵 **סכום:** ₪{result['amount']:,.2f}
📊 **מע"מ:** ₪{result['vat']:,.2f}
💰 **סה"כ:** ₪{result['total']:,.2f}
✅ **סטטוס:** {result['status']}

**הסבר:**
"""
        
        if is_exempt:
            output += """
- טיפולי שיניים רגילים **פטורים ממע"מ**
- לא צריך להוסיף מע"מ לחשבונית
- לא צריך לדווח מע"מ על טיפולים אלה
"""
        else:
            output += """
- טיפולים אסתטיים/מוצרים **חייבים במע"מ** (17%)
- יש להוסיף מע"מ לחשבונית
- יש לדווח מע"מ בדוח הדו-חודשי
"""
        
        output += "\n\n⚠️ **חשוב:** זהו ייעוץ כללי. במקרים מורכבים או לא ברורים, התייעץ עם רו\"ח."
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error calculating VAT: {e}")
        return f"שגיאה בחישוב מע\"מ: {str(e)}"


@tool
def get_tax_deadlines(month: Optional[int] = None) -> str:
    """
    Get upcoming tax deadlines for Israeli dental clinics.
    
    Args:
        month: Optional month number (1-12) to get deadlines for specific month
        
    Returns:
        Tax deadlines as formatted string
    """
    try:
        from datetime import datetime
        
        if month is None:
            month = datetime.now().month
        
        deadlines = {
            1: ["מקדמה 1/6 - עד 31/1", "דיווח מע\"מ נובמבר-דצמבר - עד 15/1"],
            2: ["דיווח מע\"מ ינואר-פברואר - עד 15/3"],
            3: ["מקדמה 2/6 - עד 31/3"],
            4: ["דיווח מע\"מ מרץ-אפריל - עד 15/5"],
            5: ["מקדמה 3/6 - עד 31/5", "דוח שנתי 2024 - עד 31/5"],
            6: ["דיווח מע\"מ מאי-יוני - עד 15/7"],
            7: ["מקדמה 4/6 - עד 31/7"],
            8: ["דיווח מע\"מ יולי-אוגוסט - עד 15/9"],
            9: ["מקדמה 5/6 - עד 30/9"],
            10: ["דיווח מע\"מ ספטמבר-אוקטובר - עד 15/11"],
            11: ["מקדמה 6/6 - עד 30/11", "דוח שנתי מורחב 2024 - עד 30/11"],
            12: ["דיווח מע\"מ נובמבר-דצמבר - עד 15/1/2026"],
        }
        
        month_names = {
            1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל",
            5: "מאי", 6: "יוני", 7: "יולי", 8: "אוגוסט",
            9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
        }
        
        output = f"""
📅 **מועדי דיווח למס - {month_names[month]} 2025**

"""
        
        if month in deadlines:
            for deadline in deadlines[month]:
                output += f"⏰ {deadline}\n"
        else:
            output += "אין מועדי דיווח מיוחדים החודש.\n"
        
        output += """

**תזכורות כלליות:**
- מקדמות מס: 6 פעמים בשנה
- דיווח מע"מ: כל חודשיים (עד ה-15)
- דוח שנתי: עד 31 במאי
- דוח מורחב: עד 30 בנובמבר (אם נדרש)

**⚠️ חשוב:** איחור בדיווח עלול לגרור קנסות וריבית פיגורים!
"""
        
        return output.strip()
        
    except Exception as e:
        logger.error(f"Error getting tax deadlines: {e}")
        return f"שגיאה בקבלת מועדי דיווח: {str(e)}"


@tool
def get_tax_optimization_tips() -> str:
    """
    Get tax optimization tips for Israeli dental clinics.
    
    Returns:
        Tax optimization tips as formatted string
    """
    return """
💡 **טיפים לאופטימיזציה מיסויית - מרפאות שיניים**

## 🎯 הוצאות מוכרות

### ✅ הוצאות שכדאי לנצל
1. **השתלמויות מקצועיות** - 100% מוכרות
2. **ביטוח מקצועי** - חובה וניתן לניכוי מלא
3. **ציוד רפואי** - פחת על פני 7-15 שנים
4. **שיווק דיגיטלי** - 100% מוכר
5. **תוכנות ניהול** - 100% מוכרות

### 📱 הוצאות חלקיות
- **רכב:** עד 33% (אם משמש גם לצרכים פרטיים)
- **טלפון:** עד 50% (אם משמש גם לצרכים פרטיים)
- **משרד בבית:** לפי שטח יחסי

## 💰 חיסכון פנסיוני

### קרן השתלמות
- **הפרשה:** עד 4.5% מהמשכורת
- **הטבה:** פטור ממס על ההפרשה
- **משיכה:** לאחר 6 שנים ללא מס

### ביטוח מנהלים
- **הפרשה:** עד 7.5% מהמשכורת
- **הטבה:** ניכוי מס על ההפרשה
- **משיכה:** בגיל פרישה

## 📊 תכנון שנתי

### לפני סוף שנת המס (31/12)
1. **רכישת ציוד** - ניצול פחת
2. **תשלום הוצאות מראש** - ניכוי מיידי
3. **הפרשות פנסיוניות** - מקסום הטבות
4. **תרומות** - ניכוי עד 30% מההכנסה

### תחילת שנה (ינואר)
1. **עדכון מקדמות** - התאמה להכנסה צפויה
2. **תכנון תזרים** - הכנה לתשלומי מס
3. **ביקורת הוצאות** - זיהוי חיסכון

## ⚠️ טעויות נפוצות

### ❌ מה לא לעשות
1. **ערבוב חשבונות** - פרטי ועסקי
2. **העדר תיעוד** - קבלות חסרות
3. **הוצאות לא מוכרות** - קנסות, הוצאות אישיות
4. **איחור בדיווח** - קנסות וריבית

### ✅ מה כן לעשות
1. **תיעוד דיגיטלי** - סריקת כל קבלה
2. **חשבון בנק נפרד** - לעסק בלבד
3. **ייעוץ רו"ח** - לפחות פעם בשנה
4. **דיווח בזמן** - הימנעות מקנסות

## 🎓 דוגמה לחיסכון

**מרפאה עם הכנסה של ₪500,000:**

**ללא אופטימיזציה:**
- מס הכנסה: ~₪150,000 (30%)

**עם אופטימיזציה:**
- הוצאות מוכרות: ₪150,000
- הפרשות פנסיוניות: ₪25,000
- הכנסה חייבת: ₪325,000
- מס הכנסה: ~₪85,000 (26%)

**חיסכון:** ₪65,000! 💰

---

## ⚠️ הצהרת אחריות

**חשוב מאוד:**
- זהו מידע כללי בלבד, לא ייעוץ מיסויי אישי
- כל מצב הוא ייחודי ודורש בדיקה מקצועית
- אל תבצע החלטות מיסויות בלי רו"ח
- Marcus הוא כלי עזר, לא תחליף לרו"ח מוסמך

**💡 המלצה חזקה:** התייעץ עם רו"ח מוסמך לתכנון מיסוי אישי.

**מצאת רו"ח?** לשכת רואי חשבון: www.icpas.org.il
"""


# Export all tools
tax_tools = [
    calculate_income_tax,
    calculate_vat_amount,
    get_tax_deadlines,
    get_tax_optimization_tips,
]

