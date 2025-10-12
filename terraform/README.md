# DentaFlow GCP Terraform Infrastructure
## Infrastructure as Code for Google Cloud Platform Deployment

**Version:** v1.0  
**Date:** October 11, 2025  
**Status:** 🟡 Development  
**HIPAA Compliant:** ✅ Yes

---

## 📋 Overview

This directory contains Terraform code to deploy the DentaFlow application infrastructure on Google Cloud Platform (GCP). The infrastructure is designed to be HIPAA-compliant, cost-effective, and scalable.

### Key Features:
- ✅ **HIPAA Compliant** - All services covered under GCP BAA
- ✅ **Multi-Environment** - Dev, Staging, Production
- ✅ **Modular Design** - Reusable Terraform modules
- ✅ **Secure by Default** - Encryption, IAM, VPC isolation
- ✅ **Cost Optimized** - 58% cheaper than AWS

---

## 🗂️ Directory Structure

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf           # Main configuration for dev
│   │   ├── variables.tf      # Variables for dev
│   │   └── terraform.tfvars  # Variable values (not committed)
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       └── terraform.tfvars
├── modules/
│   ├── cloud-run/            # Cloud Run service module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-sql/            # Cloud SQL database module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cloud-storage/        # Cloud Storage buckets module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── networking/           # VPC and networking module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/           # Monitoring and alerting module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── README.md                 # This file
```

---

## 🚀 Quick Start

### Prerequisites:

1. **Google Cloud Account** with billing enabled
2. **Terraform** installed (v1.0+)
3. **Google Cloud CLI** installed and configured
4. **GCP Project** created
5. **HIPAA BAA** signed with Google Cloud

### Installation:

```bash
# Install Terraform (if not already installed)
brew install terraform  # macOS
# or
sudo apt-get install terraform  # Ubuntu

# Install Google Cloud CLI
brew install google-cloud-sdk  # macOS
# or
curl https://sdk.cloud.google.com | bash  # Linux

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

---

## 📦 Module Descriptions

### 1. Networking Module

**Purpose:** Creates VPC, subnets, and firewall rules.

**Resources:**
- VPC network
- Subnet (10.0.0.0/24)
- Firewall rules (SSH)

**Usage:**
```hcl
module "networking" {
  source = "../../modules/networking"

  project_id = "your-project-id"
  region     = "us-central1"
}
```

---

### 2. Cloud SQL Module

**Purpose:** Creates PostgreSQL database instance with encryption and backups.

**Resources:**
- Cloud SQL instance (PostgreSQL 15)
- Database
- Secret Manager for password
- Automated backups

**Features:**
- ✅ Encryption at rest
- ✅ Automated backups (7 days)
- ✅ Private IP
- ✅ HIPAA compliant

**Usage:**
```hcl
module "cloud_sql" {
  source = "../../modules/cloud-sql"

  project_id  = "your-project-id"
  region      = "us-central1"
  db_password = var.db_password
}
```

---

### 3. Cloud Run Module

**Purpose:** Deploys containerized backend API.

**Resources:**
- Cloud Run service
- IAM permissions
- Cloud SQL connection
- Environment variables

**Features:**
- ✅ Auto-scaling (2-10 instances)
- ✅ 2 vCPU, 2GB RAM per instance
- ✅ Cloud SQL Proxy connection
- ✅ Secret Manager integration

**Usage:**
```hcl
module "cloud_run" {
  source = "../../modules/cloud-run"

  project_id         = "your-project-id"
  region             = "us-central1"
  service_name       = "dentaflow-backend"
  image_name         = "gcr.io/your-project/backend:latest"
  db_connection_name = module.cloud_sql.instance_connection_name
  db_password_secret = module.cloud_sql.db_password_secret_name
}
```

---

### 4. Cloud Storage Module

**Purpose:** Creates storage buckets for frontend and file uploads.

**Resources:**
- Frontend bucket (public, website hosting)
- Uploads bucket (private, encrypted)

**Features:**
- ✅ Encryption at rest
- ✅ Lifecycle policies
- ✅ CORS configuration
- ✅ HIPAA compliant

**Usage:**
```hcl
module "cloud_storage" {
  source = "../../modules/cloud-storage"

  project_id = "your-project-id"
  region     = "us-central1"
}
```

---

### 5. Monitoring Module

**Purpose:** Sets up monitoring, logging, and alerting.

**Resources:**
- Alert policies
- Notification channels
- Dashboards

**Features:**
- ✅ High error rate alerts
- ✅ Email notifications
- ✅ Cloud Logging integration

**Usage:**
```hcl
module "monitoring" {
  source = "../../modules/monitoring"

  project_id  = "your-project-id"
  alert_email = "alerts@dentaflow.ai"
}
```

---

## 🔧 Deployment Instructions

### Step 1: Configure Variables

Create `terraform.tfvars` in the environment directory:

```hcl
# environments/dev/terraform.tfvars
gcp_project_id = "dentaflow-dev"
gcp_region     = "us-central1"
db_password    = "your-secure-password"  # Use Secret Manager in production!
```

**⚠️ Important:** Never commit `terraform.tfvars` to git! Add it to `.gitignore`.

---

### Step 2: Initialize Terraform

```bash
cd environments/dev
terraform init
```

This will:
- Download required providers
- Initialize backend
- Set up modules

---

### Step 3: Plan Deployment

```bash
terraform plan
```

This will:
- Show what resources will be created
- Validate configuration
- Check for errors

---

### Step 4: Apply Configuration

```bash
terraform apply
```

This will:
- Create all resources
- Set up networking
- Deploy database
- Deploy application

**Expected time:** 10-15 minutes

---

### Step 5: Verify Deployment

```bash
# Get Cloud Run URL
terraform output cloud_run_url

# Test the endpoint
curl https://YOUR-CLOUD-RUN-URL/health
```

---

## 🔐 Security Best Practices

### 1. Secrets Management

**Never hardcode secrets!** Use Secret Manager:

```hcl
resource "google_secret_manager_secret" "db_password" {
  secret_id = "db-password"
  
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password  # From environment variable
}
```

**Usage:**
```bash
# Set password as environment variable
export TF_VAR_db_password="your-secure-password"

# Or use gcloud to create secret
gcloud secrets create db-password --data-file=password.txt
```

---

### 2. IAM Permissions

**Principle of least privilege:**

```hcl
resource "google_service_account" "cloud_run" {
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}

resource "google_project_iam_member" "cloud_run_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}
```

---

### 3. Network Security

**VPC isolation:**

```hcl
resource "google_compute_firewall" "deny_all" {
  name    = "deny-all-ingress"
  network = google_compute_network.main.name
  
  deny {
    protocol = "all"
  }
  
  source_ranges = ["0.0.0.0/0"]
  priority      = 65534
}
```

---

## 💰 Cost Estimation

### Development Environment:
```yaml
Cloud Run:        $10/month  (minimal traffic)
Cloud SQL:        $25/month  (db-g1-small)
Cloud Storage:    $1/month   (minimal data)
Monitoring:       $0/month   (free tier)
Total:            ~$36/month
```

### Production Environment (per clinic):
```yaml
Cloud Run:        $48/month  (auto-scaling)
Cloud SQL:        $68/month  (db-n1-standard-1)
Memorystore:      $13/month  (Redis)
Cloud Storage:    $4/month
Cloud CDN:        $80/month
Load Balancer:    $18/month
Monitoring:       $8/month
Total:            ~$239/month
```

**With optimizations:** $174/month (39% cheaper than AWS!)

---

## 🧪 Testing

### Test Plan:

1. **Unit Tests** - Terraform validate
2. **Integration Tests** - Deploy to dev
3. **Security Tests** - Scan for vulnerabilities
4. **Performance Tests** - Load testing

### Commands:

```bash
# Validate Terraform syntax
terraform validate

# Format code
terraform fmt -recursive

# Security scan (using tfsec)
tfsec .

# Cost estimation (using infracost)
infracost breakdown --path .
```

---

## 📚 Additional Resources

### Official Documentation:
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)
- [GCP HIPAA Compliance](https://cloud.google.com/security/compliance/hipaa)

### Tutorials:
- [Deploy Cloud Run with Terraform](https://dev.to/bhanufyi/deploy-google-cloud-run-with-terraform-full-guide-3fid)
- [Cloud SQL with Terraform](https://www.cloudskillsboost.google/focuses/1215)
- [GCP Multi-Tenant Architecture](https://cloud.google.com/architecture/saas-multitenant-patterns)

---

## 🐛 Troubleshooting

### Common Issues:

#### 1. "API not enabled"
**Error:**
```
Error: Error creating service: googleapi: Error 403: Cloud Run API has not been used
```

**Solution:**
```bash
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable compute.googleapis.com
```

---

#### 2. "Permission denied"
**Error:**
```
Error: Error creating instance: googleapi: Error 403: The caller does not have permission
```

**Solution:**
```bash
# Grant yourself necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:your-email@example.com" \
  --role="roles/editor"
```

---

#### 3. "Cloud SQL connection failed"
**Error:**
```
Error: Error connecting to Cloud SQL instance
```

**Solution:**
```bash
# Enable Cloud SQL Admin API
gcloud services enable sqladmin.googleapis.com

# Check Cloud SQL Proxy connection
cloud_sql_proxy -instances=YOUR_INSTANCE_CONNECTION_NAME=tcp:5432
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example:

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v1
      
      - name: Authenticate to GCP
        uses: google-github-actions/auth@v0
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Terraform Init
        run: terraform init
        working-directory: ./terraform/environments/production
      
      - name: Terraform Plan
        run: terraform plan
        working-directory: ./terraform/environments/production
      
      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: ./terraform/environments/production
```

---

## 📞 Support

### Need Help?

- **Documentation:** See [GCP_MIGRATION_PLAN.md](../GCP_MIGRATION_PLAN.md)
- **HIPAA Compliance:** See [GCP_HIPAA_COVERED_SERVICES.md](../GCP_HIPAA_COVERED_SERVICES.md)
- **GCP Support:** cloud-support@google.com
- **Project Lead:** [Your Name]

---

## ✅ Checklist

### Before Deployment:
- [ ] GCP project created
- [ ] Billing enabled
- [ ] HIPAA BAA signed
- [ ] APIs enabled
- [ ] Service accounts created
- [ ] Secrets configured

### After Deployment:
- [ ] Health check passing
- [ ] Database connected
- [ ] Monitoring configured
- [ ] Alerts working
- [ ] Backups enabled
- [ ] Documentation updated

---

**Status:** 🟡 Ready for development deployment  
**Next Step:** Deploy to dev environment  
**Estimated Time:** 15 minutes

🚀 **Let's deploy to GCP!**

