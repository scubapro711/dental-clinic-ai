# 🔐 AWS Credentials Setup Guide
## Step-by-Step Instructions for Creating API Access

---

## 🎯 **הלינק המדויק ליצירת AWS Credentials:**

### **שלב 1: כניסה ל-AWS Console**
```
https://console.aws.amazon.com/
```

### **שלב 2: מעבר ל-IAM (Identity and Access Management)**
```
https://console.aws.amazon.com/iam/home
```

### **שלב 3: יצירת IAM User חדש**
```
https://console.aws.amazon.com/iam/home#/users$new?step=details
```

---

## 📋 **הוראות צעד אחר צעד:**

### **שלב 1: יצירת IAM User**

1. **לחץ על הלינק:** https://console.aws.amazon.com/iam/home#/users$new?step=details

2. **הגדר שם משתמש:**
   - User name: `dental-clinic-ai-deploy`
   - Access type: ✅ **Programmatic access** (חובה!)

3. **לחץ Next: Permissions**

### **שלב 2: הגדרת הרשאות**

1. **בחר: "Attach existing policies directly"**

2. **חפש והוסף את המדיניות הבאות:**
   ```
   ✅ AmazonECS_FullAccess
   ✅ AmazonRDS_FullAccess  
   ✅ AmazonElastiCacheFullAccess
   ✅ AmazonEC2FullAccess
   ✅ AmazonRoute53FullAccess
   ✅ AWSCertificateManagerFullAccess
   ✅ SecretsManagerReadWrite
   ✅ CloudWatchFullAccess
   ✅ IAMFullAccess
   ✅ AmazonS3FullAccess
   ```

3. **לחץ Next: Tags** (אופציונלי)

4. **לחץ Next: Review**

### **שלב 3: סיום ויצירת Access Keys**

1. **לחץ "Create user"**

2. **⚠️ חשוב מאוד:** בעמוד הבא תקבל:
   - **Access Key ID** 
   - **Secret Access Key**
   
3. **💾 שמור את שני המפתחות מיד!** 
   - לחץ "Download .csv" או העתק ידנית
   - **זו ההזדמנות היחידה לראות את Secret Key!**

---

## 🔑 **מה תקבל:**

```
AWS_ACCESS_KEY_ID=AKIA....... (20 תווים)
AWS_SECRET_ACCESS_KEY=....... (40 תווים)
```

---

## 🛡️ **אבטחה חשובה:**

### **אל תשתף את המפתחות:**
- ❌ אל תשלח בווטסאפ/אימייל
- ❌ אל תשמור בקבצי טקסט
- ✅ שמור רק ב-GitHub Secrets

### **הגדרת GitHub Secrets:**
1. לך לרפוזיטורי: https://github.com/scubapro711/dental-clinic-ai
2. Settings → Secrets and variables → Actions
3. לחץ "New repository secret"
4. הוסף:
   ```
   Name: AWS_ACCESS_KEY_ID
   Value: [המפתח שקיבלת]
   
   Name: AWS_SECRET_ACCESS_KEY  
   Value: [הסוד שקיבלת]
   
   Name: AWS_REGION
   Value: us-east-1
   ```

---

## 🧪 **בדיקת תקינות:**

לאחר יצירת המפתחות, תוכל לבדוק אותם:

```bash
# הגדרת AWS CLI
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1

# בדיקה
aws sts get-caller-identity
```

אם הכל תקין, תקבל תגובה עם:
- Account ID
- User ARN
- User ID

---

## 🚀 **לאחר ההגדרה:**

1. **הגדר את GitHub Secrets**
2. **הרץ deployment:** `./scripts/deploy-to-aws.sh`
3. **המערכת תפרוס אוטומטית ל-AWS!**

---

## 📞 **אם יש בעיות:**

### **שגיאות נפוצות:**
- **"Access Denied"** → בדוק הרשאות IAM
- **"Invalid credentials"** → בדוק שהמפתחות נכונים
- **"Region not found"** → הגדר AWS_REGION=us-east-1

### **לינקים לעזרה:**
- AWS IAM Documentation: https://docs.aws.amazon.com/iam/
- AWS CLI Setup: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html

---

**🎯 תתחיל עם הלינק הזה:** https://console.aws.amazon.com/iam/home#/users$new?step=details
