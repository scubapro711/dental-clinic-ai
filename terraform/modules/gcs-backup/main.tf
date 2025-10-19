# GCS Bucket for Database Backups
# This module creates a Google Cloud Storage bucket for storing database backups

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# GCS Bucket for Backups
resource "google_storage_bucket" "backup_bucket" {
  name          = "${var.project_id}-database-backups"
  location      = var.location
  project       = var.project_id
  
  # Storage class
  storage_class = "STANDARD"
  
  # Uniform bucket-level access
  uniform_bucket_level_access = true
  
  # Versioning
  versioning {
    enabled = true
  }
  
  # Lifecycle rules
  lifecycle_rule {
    condition {
      age = var.retention_days
    }
    action {
      type = "Delete"
    }
  }
  
  lifecycle_rule {
    condition {
      age = 7
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
  
  # Encryption
  encryption {
    default_kms_key_name = var.kms_key_name
  }
  
  # Labels
  labels = {
    environment = var.environment
    purpose     = "database-backups"
    managed_by  = "terraform"
  }
}

# IAM binding for backup service account
resource "google_storage_bucket_iam_member" "backup_writer" {
  bucket = google_storage_bucket.backup_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.backup_service_account}"
}

# IAM binding for Cloud SQL service account
resource "google_storage_bucket_iam_member" "cloudsql_backup" {
  bucket = google_storage_bucket.backup_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.cloudsql_service_account}"
}

# Outputs
output "bucket_name" {
  description = "Name of the backup bucket"
  value       = google_storage_bucket.backup_bucket.name
}

output "bucket_url" {
  description = "URL of the backup bucket"
  value       = google_storage_bucket.backup_bucket.url
}

output "bucket_self_link" {
  description = "Self link of the backup bucket"
  value       = google_storage_bucket.backup_bucket.self_link
}

