# Pull Request

## 📝 תיאור השינוי

תיאור קצר של מה השתנה ולמה.

## 🏷️ סוג השינוי

- [ ] 🐛 Bug fix (תיקון באג)
- [ ] ✨ Feature חדש (תכונה חדשה)
- [ ] 💥 Breaking change (שינוי ששובר תאימות)
- [ ] 🏗️ שינוי ארכיטקטוני (framework, database, deployment)
- [ ] 👤 הוספה/הסרה/שינוי של agent
- [ ] 📚 עדכון תיעוד בלבד

## ✅ Checklist - שינויים בקוד

- [ ] הקוד עוקב אחרי style guidelines של הפרויקט
- [ ] עשיתי self-review
- [ ] הוספתי comments למקומות מורכבים
- [ ] הסרתי קוד debug (console.log, print statements)
- [ ] הקוד עובד locally

## 🧪 Checklist - בדיקות

- [ ] הוספתי tests חדשים לתכונות חדשות
- [ ] כל ה-tests עוברים (`pytest backend/tests/`)
- [ ] Frontend-backend sync test עובר
- [ ] בדקתי ידנית שהכל עובד

## 📚 Checklist - תיעוד

- [ ] עדכנתי README (אם צריך)
- [ ] עדכנתי תוכנית עבודה (אם הוספתי/הסרתי features)
- [ ] עדכנתי FEATURE_INVENTORY.md (אם הוספתי/הסרתי features)
- [ ] עדכנתי ARCHITECTURE_CHANGELOG.md (אם שיניתי ארכיטקטורה)
- [ ] יצרתי ADR (אם קיבלתי החלטה חשובה)

## 💬 Checklist - Commit Message

- [ ] הודעת ה-commit עוקבת אחרי conventional commits
- [ ] כוללת Manus-Session-ID
- [ ] כוללת Human-Initiator
- [ ] ה-body מסביר "למה" ולא רק "מה"

## 🔍 Checklist - ניתוח השפעה

- [ ] הרצתי `python scripts/check_work_plan_sync.py`
- [ ] אין breaking changes, **או** תיעדתי אותם ב-ADR
- [ ] עדכנתי frontend (אם שיניתי agents ב-backend)
- [ ] עדכנתי tests (אם שיניתי התנהגות של agents)

## 🔄 Checklist - Rollback Plan

- [ ] תיעדתי נוהל rollback (אם יש breaking change)
- [ ] בדקתי את נוהל ה-rollback (אם זה שינוי קריטי)

## 🤖 Manus Session

**Manus-Session-ID:** [הכנס Session ID]  
**Link:** https://app.manus.im/sessions/[SESSION_ID]

## 📸 Screenshots (אם שינית UI)

[הוסף screenshots כאן]

## 📝 הערות נוספות

[כל מידע נוסף שחשוב]

---

## 🎯 למבצע ה-Review

### מה לבדוק:
- [ ] הקוד ברור וקריא
- [ ] יש tests מספיקים
- [ ] התיעוד מעודכן
- [ ] אין security issues
- [ ] ביצועים סבירים

### שאלות לשאול:
- האם זה פותר את הבעיה?
- האם זה יכול לשבור משהו?
- האם יש דרך פשוטה יותר?
