# 📥 מדריך צעד-אחר-צעד להורדת Pragtech Module

## 🎯 הבעיה
כפתור "Download" בחשבונית הוריד רק את החשבונית, לא את המודול.

## ✅ הפתרון - 3 דרכים

---

## דרך 1: דרך Odoo Apps - My Purchases (הכי פשוט!)

### צעד 1: היכנס ל-Odoo Apps
1. פתח דפדפן
2. לך ל: **https://apps.odoo.com/**
3. לחץ על **"Sign in"** (למעלה מימין)
4. הזן את המייל והסיסמה שלך (אותם שהשתמשת ברכישה)

### צעד 2: לך לדף הרכישות שלך
1. אחרי שנכנסת, לחץ על **התמונה שלך** (למעלה מימין)
2. בחר **"My Purchases"** או **"My Apps"**
3. או לך ישירות ל: **https://apps.odoo.com/my/purchases**

### צעד 3: מצא את המודול
1. תראה רשימה של כל המודולים שרכשת
2. חפש: **"Dental Clinic Management"**
3. או: **"pragtech_dental_management"**

### צעד 4: הורד
1. ליד המודול יהיה כפתור **"Download"** או **"Download ZIP"**
2. לחץ עליו
3. הקובץ יורד: `pragtech_dental_management-19.0.zip`

---

## דרך 2: דרך דף התמיכה של המודול

### צעד 1: היכנס ל-Odoo Apps
1. לך ל: **https://apps.odoo.com/**
2. התחבר (Sign in)

### צעד 2: לך לדף התמיכה
1. לך ישירות ל: **https://apps.odoo.com/apps/support/263093**
2. או:
   - לך לדף המודול: https://apps.odoo.com/apps/modules/19.0/pragtech_dental_management
   - לחץ על **"You bought this module and need support? Click here!"**

### צעד 3: הורד
1. בדף התמיכה, תראה:
   - **"Download"** button
   - **"Module Files"** section
   - **"Technical Information"**
2. לחץ על **"Download"**
3. הקובץ יורד

---

## דרך 3: צור קשר עם Pragmatic TechSoft (אם כלום לא עובד)

### אופציה A: דרך Odoo Support Ticket

1. לך ל: **https://apps.odoo.com/apps/support/263093**
2. לחץ על **"Create Ticket"** או **"Contact Support"**
3. כתוב:
   ```
   Subject: Cannot download module - Need download link
   
   Hi,
   
   I purchased Pragtech Dental Management v19.0 but cannot find the download button.
   
   Invoice: 2025/10/004466
   Date: 10/05/2025
   Amount: $496.83
   
   Please send me the download link or the ZIP file.
   
   Thank you
   ```

### אופציה B: מייל ישיר ל-Pragmatic TechSoft

שלח מייל ל: **support@pragtech.co.in**

```
Subject: Download Request - Pragtech Dental Management v19.0

Hi Pragmatic TechSoft team,

I purchased your Dental Clinic Management module for Odoo 19.0 
but I'm having trouble downloading it.

Purchase Details:
- Invoice Number: 2025/10/004466
- Date: 10/05/2025
- Amount: $496.83
- Version: 19.0

Could you please send me:
1. Direct download link, or
2. The ZIP file attached to email

My registered email: [הכנס את המייל שלך]

Thank you,
[השם שלך]
```

### אופציה C: טלפון

התקשר ל: **+91-79-40327172**

אמור:
```
"Hi, I purchased Pragtech Dental Management module for Odoo 19.
Invoice 2025/10/004466.
I need help downloading the module files."
```

---

## 🔍 איך לדעת שהורדת את הקובץ הנכון?

### ✅ קובץ נכון:
- שם: `pragtech_dental_management-19.0.zip` (או דומה)
- גודל: **5-15 MB** (לא 100KB!)
- סוג: **ZIP file**
- תוכן: תיקייה עם קבצי Python, XML, וכו'

### ❌ קובץ לא נכון:
- שם: `2025_10_004466.pdf`
- גודל: **100-200 KB**
- סוג: **PDF**
- תוכן: החשבונית (לא המודול!)

---

## 🎯 מה לעשות אחרי ההורדה?

### 1. חלץ את הקובץ
```bash
unzip pragtech_dental_management-19.0.zip
```

תקבל תיקייה:
```
pragtech_dental_management/
├── __init__.py
├── __manifest__.py
├── models/
├── views/
├── security/
├── data/
├── static/
└── README.md
```

### 2. בדוק שזה הקובץ הנכון
```bash
cd pragtech_dental_management
ls -la
```

תראה:
- קבצי `.py` (Python)
- קבצי `.xml` (Views)
- תיקיות: models, views, security, data, static

### 3. מוכן להתקנה!
עכשיו אפשר להתקין את Odoo 19 ולהעתיק את המודול.

---

## ❓ שאלות נפוצות

### ש: איפה אני רואה את הרכישות שלי?
**ת:** https://apps.odoo.com/my/purchases (אחרי שנכנסת)

### ש: אין לי כפתור Download
**ת:** 
1. וודא שנכנסת עם המייל הנכון
2. נסה דפדפן אחר
3. נקה cache
4. צור קשר עם התמיכה

### ש: הקובץ שהורדתי הוא PDF
**ת:** זו החשבונית, לא המודול. נסה דרך 2 או 3.

### ש: הקובץ קטן מדי (100KB)
**ת:** זו לא המודול. המודול צריך להיות 5-15 MB.

### ש: לא מצליח להוריד בכלל
**ת:** צור קשר עם Pragmatic TechSoft (דרך 3)

---

## 📞 אנשי קשר

### Odoo Support
- **אתר:** https://www.odoo.com/help
- **מייל:** support@odoo.com

### Pragmatic TechSoft Support
- **אתר:** http://pragtech.co.in
- **מייל:** support@pragtech.co.in
- **טלפון:** +91-79-40327172
- **דף תמיכה:** https://apps.odoo.com/apps/support/263093

---

## ✅ Checklist

- [ ] נכנסתי ל-Odoo Apps
- [ ] הלכתי ל-My Purchases
- [ ] מצאתי את Pragtech Dental Management
- [ ] לחצתי על Download
- [ ] הורדתי קובץ ZIP (לא PDF!)
- [ ] הקובץ הוא 5-15 MB (לא 100KB!)
- [ ] חילצתי את הקובץ
- [ ] ראיתי תיקייה עם קבצי Python
- [ ] מוכן להתקנה!

---

## 🚨 אם כלום לא עובד

**צור קשר איתי** ואני אעזור לך:
1. לפתוח ticket ב-Odoo
2. לשלוח מייל ל-Pragmatic TechSoft
3. למצוא דרך חלופית

**לא תישאר תקוע!** 💪

---

**עודכן:** 2025-10-06  
**מחבר:** Manus AI Agent
