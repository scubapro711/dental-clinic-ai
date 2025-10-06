# 🚀 AWS EC2 Deployment Guide - Odoo 19

**זמן משוער:** 15-20 דקות  
**קושי:** קל (צעד אחר צעד)

---

## שלב 1: הקמת EC2 Instance (5 דקות)

### 1.1 התחבר ל-AWS Console
1. גש ל: https://console.aws.amazon.com/
2. התחבר עם המשתמש שלך
3. בחר Region: **us-east-1** (צפון וירג'יניה)

### 1.2 צור EC2 Instance
1. לך ל: **EC2 Dashboard**
2. לחץ על **"Launch Instance"**

### 1.3 הגדרות Instance

**Name:** `dental-odoo-prod`

**Application and OS Images (AMI):**
- בחר: **Ubuntu Server 22.04 LTS**
- Architecture: **64-bit (x86)**

**Instance type:**
- בחר: **t3.medium**
  - 2 vCPUs
  - 4 GB RAM
  - עלות: ~$0.04/שעה (~$30/חודש)

**Key pair:**
- אם אין לך: לחץ **"Create new key pair"**
- Name: `dental-odoo-key`
- Type: **RSA**
- Format: **.pem** (למק/לינוקס) או **.ppk** (לWindows)
- **⚠️ שמור את הקובץ! לא תוכל להוריד אותו שוב**

**Network settings:**
- VPC: השאר ברירת מחדל
- Subnet: השאר ברירת מחדל
- Auto-assign public IP: **Enable**

**Firewall (Security groups):**
- בחר: **Select existing security group**
- בחר: **sg-0158d82c94e44e5a3** (dental-odoo-sg)
  - אם לא רואה אותו, צור חדש עם החוקים הבאים:
    - SSH (22) - 0.0.0.0/0
    - HTTP (80) - 0.0.0.0/0
    - HTTPS (443) - 0.0.0.0/0
    - Custom TCP (8069) - 0.0.0.0/0

**Configure storage:**
- Size: **30 GB**
- Volume type: **gp3**

### 1.4 השק Instance
1. לחץ **"Launch instance"**
2. המתן 1-2 דקות עד שה-Instance יהיה **Running**
3. **העתק את ה-Public IPv4 address** (למשל: 3.85.123.45)

---

## שלב 2: התחברות ל-Instance (2 דקות)

### 2.1 מ-Mac/Linux:
```bash
# תן הרשאות לקובץ המפתח
chmod 400 ~/Downloads/dental-odoo-key.pem

# התחבר ל-EC2
ssh -i ~/Downloads/dental-odoo-key.pem ubuntu@[PUBLIC-IP]
```

### 2.2 מ-Windows:
- השתמש ב-PuTTY עם הקובץ .ppk
- או WSL עם הפקודה למעלה

---

## שלב 3: התקנת Docker (5 דקות)

### 3.1 הרץ את הפקודות הבאות:

```bash
# עדכון המערכת
sudo apt-get update
sudo apt-get upgrade -y

# התקנת Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# הוספת המשתמש לקבוצת docker
sudo usermod -aG docker ubuntu

# התקנת Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# אימות התקנה
docker --version
docker-compose --version
```

**צפוי לראות:**
```
Docker version 24.x.x
Docker Compose version v2.20.0
```

### 3.2 התנתק והתחבר מחדש
```bash
exit
ssh -i ~/Downloads/dental-odoo-key.pem ubuntu@[PUBLIC-IP]
```

---

## שלב 4: העלאת קבצי Odoo (3 דקות)

### 4.1 מהמחשב המקומי שלך:

```bash
# העתק את כל תיקיית הפרויקט
scp -i ~/Downloads/dental-odoo-key.pem -r \
  /path/to/dental-clinic-working/pragtech_dental_management \
  ubuntu@[PUBLIC-IP]:/home/ubuntu/

scp -i ~/Downloads/dental-odoo-key.pem \
  /path/to/dental-clinic-working/docker-compose-odoo19.yml \
  ubuntu@[PUBLIC-IP]:/home/ubuntu/docker-compose.yml

scp -i ~/Downloads/dental-odoo-key.pem \
  /path/to/dental-clinic-working/odoo.conf \
  ubuntu@[PUBLIC-IP]:/home/ubuntu/
```

**או אפשר לעשות זאת דרך Git:**

```bash
# על ה-EC2
cd /home/ubuntu
git clone https://github.com/scubapro711/dental-clinic-ai.git
cd dental-clinic-ai
git checkout v14.0-agent-driven-system

# העתק את הקבצים הנדרשים
cp docker-compose-odoo19.yml ~/docker-compose.yml
cp odoo.conf ~/
cp -r pragtech_dental_management ~/
```

---

## שלב 5: הרצת Odoo (2 דקות)

### 5.1 על ה-EC2:

```bash
cd /home/ubuntu

# צור תיקיות נדרשות
mkdir -p odoo-data
mkdir -p postgres-data
mkdir -p addons

# העתק את Pragtech לaddons
cp -r pragtech_dental_management addons/

# הרץ את Odoo
docker-compose up -d

# בדוק שהכל רץ
docker-compose ps
docker-compose logs -f odoo
```

**צפוי לראות:**
```
odoo-web    running
odoo-db     running
```

### 5.2 המתן ~30 שניות עד שOdoo יסיים להתקין

---

## שלב 6: גישה ל-Odoo (1 דקה)

### 6.1 פתח דפדפן:
```
http://[PUBLIC-IP]:8069
```

### 6.2 צור Database:
1. **Database Name:** `dental_prod`
2. **Email:** הדוא"ל שלך
3. **Password:** סיסמה חזקה (שמור אותה!)
4. **Language:** English (או Hebrew)
5. **Country:** Israel
6. לחץ **"Create database"**

### 6.3 התקן Pragtech Module:
1. לך ל: **Apps**
2. חפש: **"Pragtech"** או **"Dental"**
3. לחץ **"Install"**
4. המתן 1-2 דקות

---

## שלב 7: טעינת נתוני דמו (אופציונלי)

### 7.1 דרך ממשק Odoo:
1. לך ל: **Patients**
2. צור 10 מטופלים ידנית
3. לך ל: **Appointments**
4. צור 20 תורים

### 7.2 או דרך סקריפט (מתקדם):
```python
# נכין סקריפט Python לטעינת נתונים
```

---

## שלב 8: חיבור ה-Backend (5 דקות)

### 8.1 עדכן את הקונפיגורציה:

```bash
# במחשב המקומי, ערוך:
# backend/.env

ODOO_URL=http://[PUBLIC-IP]:8069
ODOO_DB=dental_prod
ODOO_USERNAME=admin
ODOO_PASSWORD=[הסיסמה שיצרת]
```

### 8.2 הרץ טסטים:

```bash
cd backend
pytest tests/test_odoo_integration.py -v
```

**צפוי לראות:**
```
72 tests passed ✅
```

---

## ✅ סיימנו!

### מה יש לך עכשיו:
- ✅ EC2 Instance רץ על AWS
- ✅ Odoo 19 מותקן ועובד
- ✅ Pragtech Module מותקן
- ✅ נגיש דרך: `http://[PUBLIC-IP]:8069`
- ✅ Backend יכול להתחבר

### הצעדים הבאים:
1. ⏳ להתקין Cognito Authentication
2. ⏳ לפתח Sarah Agent
3. ⏳ לסיים את ה-Dashboard

---

## 🔧 Troubleshooting

### בעיה: לא מצליח להתחבר ל-EC2
**פתרון:**
```bash
# בדוק שה-Security Group מאפשר SSH
aws ec2 describe-security-groups --group-ids sg-0158d82c94e44e5a3
```

### בעיה: Odoo לא עולה
**פתרון:**
```bash
# בדוק לוגים
docker-compose logs odoo

# אתחל מחדש
docker-compose restart odoo
```

### בעיה: לא רואה את Pragtech ב-Apps
**פתרון:**
```bash
# וודא שהמודול בתיקייה הנכונה
ls -la /home/ubuntu/addons/pragtech_dental_management

# אתחל את Odoo
docker-compose restart odoo
```

---

## 💰 עלויות

**EC2 t3.medium:**
- שעתי: $0.0416
- יומי: ~$1
- חודשי: ~$30

**EBS Storage (30GB):**
- חודשי: ~$3

**סה"כ:** ~$33/חודש

---

## 🔒 אבטחה

### מומלץ:
1. **שנה את הסיסמה של Odoo** לסיסמה חזקה
2. **הגבל SSH** רק ל-IP שלך (לא 0.0.0.0/0)
3. **הפעל HTTPS** עם Let's Encrypt
4. **גיבויים אוטומטיים** של ה-database

---

**בהצלחה! 🚀**
