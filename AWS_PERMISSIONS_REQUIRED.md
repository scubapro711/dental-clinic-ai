# 🔐 רשימת הרשאות AWS נדרשות לפריסה מלאה

## 📋 הרשאות שכבר יש למשתמש:
✅ **AmazonEC2ContainerRegistryFullAccess**  
✅ **AmazonSQSFullAccess**

---

## 🚨 הרשאות נוספות שצריך להוסיף:

### **הרשאות חובה לפריסה:**

#### **1. EC2 & VPC (תשתית רשת)**
```
AmazonEC2FullAccess
```
**או בפירוט:**
- `ec2:DescribeAvailabilityZones`
- `ec2:DescribeVpcs`
- `ec2:CreateVpc`
- `ec2:DescribeSubnets`
- `ec2:CreateSubnet`
- `ec2:DescribeSecurityGroups`
- `ec2:CreateSecurityGroup`
- `ec2:AuthorizeSecurityGroupIngress`
- `ec2:DescribeInternetGateways`
- `ec2:CreateInternetGateway`
- `ec2:AttachInternetGateway`

#### **2. ECS (Container Services)**
```
AmazonECS_FullAccess
```

#### **3. RDS (Database)**
```
AmazonRDSFullAccess
```

#### **4. ElastiCache (Redis)**
```
AmazonElastiCacheFullAccess
```

#### **5. Application Load Balancer**
```
ElasticLoadBalancingFullAccess
```

#### **6. IAM (Identity Management)**
```
IAMFullAccess
```
**או לפחות:**
- `iam:CreateRole`
- `iam:AttachRolePolicy`
- `iam:PassRole`
- `iam:GetRole`

#### **7. CloudWatch (Monitoring & Logs)**
```
CloudWatchFullAccess
CloudWatchLogsFullAccess
```

#### **8. Secrets Manager (סודות)**
```
SecretsManagerReadWrite
```

#### **9. KMS (הצפנה)**
```
AWSKeyManagementServicePowerUser
```

#### **10. SNS (התראות)**
```
AmazonSNSFullAccess
```

---

## 🎯 **הדרך הקלה ביותר - הוספת Policy אחד:**

### **PowerUserAccess (מומלץ לפיתוח)**
```
PowerUserAccess
```
**זה נותן גישה לכמעט הכל חוץ מ-IAM management**

### **או AdministratorAccess (הכי פשוט)**
```
AdministratorAccess
```
**⚠️ זה נותן גישה מלאה - השתמש בזהירות!**

---

## 📝 **איך להוסיף הרשאות ב-AWS Console:**

### **שלב 1: כניסה ל-IAM**
```
https://console.aws.amazon.com/iam/home#/users/Scubapro711_Dev_API
```

### **שלב 2: הוספת Policies**
1. לחץ על **"Add permissions"**
2. בחר **"Attach existing policies directly"**
3. חפש וסמן את ה-policies הבאים:

#### **רשימה מינימלית (מומלץ):**
```
✅ AmazonEC2FullAccess
✅ AmazonECS_FullAccess  
✅ AmazonRDSFullAccess
✅ AmazonElastiCacheFullAccess
✅ ElasticLoadBalancingFullAccess
✅ CloudWatchFullAccess
✅ SecretsManagerReadWrite
✅ AWSKeyManagementServicePowerUser
✅ AmazonSNSFullAccess
```

#### **או פשוט אחד:**
```
✅ PowerUserAccess
```

### **שלב 3: אישור**
לחץ **"Add permissions"**

---

## 🔍 **בדיקת הרשאות לאחר ההוספה:**

```bash
# בדיקה שהכל עובד:
aws ec2 describe-availability-zones
aws ecs list-clusters  
aws rds describe-db-instances
```

אם כל הפקודות עובדות - אתה מוכן לפריסה! 🚀

---

## ⚡ **לאחר הוספת ההרשאות:**

```bash
# חזרה לפריסה:
cd /home/ubuntu/dental-clinic-ai/infrastructure/terraform/aws
terraform plan -var="environment=prod" -var="aws_region=us-east-1"
terraform apply -var="environment=prod" -var="aws_region=us-east-1"
```

---

**🎯 המלצה: תתחיל עם PowerUserAccess - זה הכי פשוט ובטוח לפיתוח!**
