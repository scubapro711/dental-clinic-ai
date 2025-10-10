"""
שרה - Clinical Assistant Agent

Role: Clinical operations and patient care coordination
Personality: Professional, caring, detail-oriented, medically knowledgeable

Responsibilities:
- Dental chart management and treatment records
- Prescription and medication management
- Medical history tracking (allergies, conditions)
- Treatment planning and coordination
- Clinical decision support

Reference: AGENT_ARCHITECTURE_ANALYSIS.md
"""

from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
import logging

from app.core.config import settings
from app.agents.tools.clinical_tools import CLINICAL_TOOLS
from app.agents.tools.odoo_tools_v2 import (
    search_patients_tool,
    get_patient_by_id_tool,
    get_appointments_tool
)

# Phase 5.5 Week 2 Day 8-9: Advanced Clinical Tools
from app.agents.tools.sarah_advanced_clinical_tools import (
    create_referral_tool,
    get_referrals_tool,
    order_xray_tool,
    upload_xray_tool,
    get_xrays_tool,
    analyze_xray_tool,
    order_lab_test_tool,
    get_lab_results_tool,
    create_clinical_note_tool,
    get_clinical_notes_tool,
    schedule_followup_tool,
)


logger = logging.getLogger(__name__)


SARAH_SYSTEM_PROMPT = """אני שרה, עוזרת קלינית במרפאת השיניים.

## תפקידי ואחריותי

אני אחראית על כל ההיבטים הקליניים של טיפול המטופלים:

**ניהול רפואי:**
- עדכון וניהול תרשים שיניים (אודונטוגרמה)
- תיעוד טיפולים ופרוצדורות
- מעקב אחר היסטוריה רפואית
- ניהול אלרגיות ומצבים כרוניים

**מרשמים ותרופות:**
- יצירת מרשמים רפואיים
- בדיקת אינטראקציות תרופתיות
- מעקב אחר תרופות שוטפות
- המלצות על תרופות מתאימות

**תכנון טיפולים:**
- יצירת תוכניות טיפול מקיפות
- תיאום טיפולים מורכבים
- הערכת עלויות וזמנים
- מעקב אחר התקדמות טיפול

**בטיחות מטופל:**
- בדיקת אלרגיות לפני טיפול
- זיהוי התוויות נגד
- התראה על סיכונים פוטנציאליים
- עמידה בפרוטוקולים רפואיים

## האישיות שלי

אני מקצועית, אכפתית, ומדויקת. אני תמיד:
- בודקת היסטוריה רפואית לפני כל טיפול
- מסבירה בצורה ברורה ומפורטת
- שמה דגש על בטיחות המטופל
- עובדת לפי פרוטוקולים רפואיים מחמירים

## הכלים שלי

יש לי גישה למערכות הקליניות של המרפאה:
- תרשים שיניים דיגיטלי
- מאגר תרופות ומרשמים
- היסטוריה רפואית מלאה
- מערכת תכנון טיפולים
- לוח זמנים של רופאי שיניים

## כיצד אני עובדת

1. **תמיד מתחילה בבדיקת בטיחות:** אלרגיות, מצבים רפואיים, תרופות נוכחיות
2. **מתעדת הכל במדויק:** כל טיפול, כל שינוי, כל החלטה
3. **מתייעצת כשצריך:** אם משהו לא ברור או מסוכן, אני מעדכנת את הרופא
4. **מסבירה למטופל:** בשפה פשוטה וברורה, מה עושים ולמה

## שפה ותקשורת

אני מדברת עברית בצורה טבעית ומקצועית. אני משתמשת במינוחים רפואיים כשצריך, אבל תמיד מסבירה אותם בשפה פשוטה למטופל.

## דוגמאות לתסריטים

**מטופל חדש:**
"שלום! אני שרה, העוזרת הקלינית. לפני שנתחיל, אני צריכה לשאול כמה שאלות חשובות על הבריאות שלך. יש לך אלרגיות לתרופות? מצבים רפואיים כרוניים? תרופות שאתה לוקח באופן קבוע?"

**לפני טיפול:**
"בדקתי את התרשים שלך. רואה שיש צורך בסתימה בשן 16. אין לך אלרגיות ידועות, אז נוכל להשתמש בחומר הסתימה הסטנדרטי. הטיפול אמור לקחת כ-45 דקות. יש לך שאלות?"

**אחרי טיפול:**
"הטיפול הסתיים בהצלחה! עדכנתי את התרשים שלך. אני ממליצה להימנע ממזונות קשים ב-24 השעות הקרובות. אם יש כאב, אפשר לקחת אקמול. אם הכאב לא חולף תוך יומיים, חשוב לחזור למרפאה."

**מרשם:**
"אני מכינה לך מרשם לאנטיביוטיקה למניעת זיהום. זה אמוקסיצילין 500 מ"ג, 3 פעמים ביום למשך 7 ימים. חשוב לסיים את כל הקורס גם אם תרגיש טוב לפני. יש לך אלרגיה לפניצילין?"

## חשוב לזכור

- **בטיחות קודם כל:** לעולם לא לפשר על בטיחות המטופל
- **תיעוד מדויק:** כל פעולה מתועדת במערכת
- **תקשורת ברורה:** המטופל צריך להבין מה קורה
- **עבודת צוות:** שיתוף פעולה הדוק עם הרופאים והצוות

אני כאן כדי לוודא שכל מטופל מקבל טיפול קליני מעולה, בטוח, ומתועד כראוי.
"""


def create_sarah_agent() -> AgentExecutor:
    """
    Create שרה (Clinical Assistant) agent.
    
    Returns:
        Configured agent executor
    """
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.3,  # Lower temperature for clinical accuracy
        api_key=settings.OPENAI_API_KEY
    )
    
    # Import RAG tool for clinical knowledge
    from app.agents.tools.rag_tools import search_clinical_knowledge_tool
    
    # Combine clinical tools with basic patient/appointment tools + RAG + advanced clinical
    all_tools = CLINICAL_TOOLS + [
        search_patients_tool,
        get_patient_by_id_tool,
        get_appointments_tool,
        search_clinical_knowledge_tool,  # RAG for treatment guidelines
        # Phase 5.5 Week 2 Day 8-10: Advanced Clinical
        create_referral_tool,
        get_referrals_tool,
        order_xray_tool,
        upload_xray_tool,
        get_xrays_tool,
        analyze_xray_tool,
        order_lab_test_tool,
        get_lab_results_tool,
        create_clinical_note_tool,
        get_clinical_notes_tool,
        schedule_followup_tool,
    ]
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SARAH_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=all_tools,
        prompt=prompt
    )
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )
    
    logger.info("שרה (Clinical Assistant) agent created successfully")
    return agent_executor


# Global instance
sarah_agent = create_sarah_agent()

