# Cloud Scheduler for Database Backups
# This module creates a Cloud Scheduler job that triggers database backups daily

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Service Account for Cloud Scheduler
resource "google_service_account" "backup_scheduler" {
  account_id   = "backup-scheduler"
  display_name = "Database Backup Scheduler"
  description  = "Service account for running scheduled database backups"
}

# Grant permissions to the service account
resource "google_project_iam_member" "backup_scheduler_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.backup_scheduler.email}"
}

resource "google_project_iam_member" "backup_scheduler_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backup_scheduler.email}"
}

resource "google_project_iam_member" "backup_scheduler_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.backup_scheduler.email}"
}

# Cloud Scheduler Job - Daily Database Backup
resource "google_cloud_scheduler_job" "daily_backup" {
  name        = "daily-database-backup"
  description = "Trigger daily database backup at 2 AM UTC"
  schedule    = "0 2 * * *"  # Daily at 2:00 AM UTC
  time_zone   = "UTC"
  region      = var.region

  retry_config {
    retry_count = 3
    min_backoff_duration = "5s"
    max_backoff_duration = "1h"
    max_retry_duration   = "2h"
    max_doublings        = 5
  }

  http_target {
    uri         = var.backup_job_url
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      backup_type = "full"
      retention_days = 30
      notify_slack = true
    }))

    oidc_token {
      service_account_email = google_service_account.backup_scheduler.email
      audience              = var.backup_job_url
    }
  }
}

# Cloud Scheduler Job - Weekly Full Backup (Sunday)
resource "google_cloud_scheduler_job" "weekly_full_backup" {
  name        = "weekly-full-database-backup"
  description = "Trigger full database backup every Sunday at 1 AM UTC"
  schedule    = "0 1 * * 0"  # Every Sunday at 1:00 AM UTC
  time_zone   = "UTC"
  region      = var.region

  retry_config {
    retry_count = 3
    min_backoff_duration = "5s"
    max_backoff_duration = "1h"
    max_retry_duration   = "3h"
    max_doublings        = 5
  }

  http_target {
    uri         = var.backup_job_url
    http_method = "POST"
    
    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      backup_type = "full"
      retention_days = 90
      notify_slack = true
      verify_integrity = true
    }))

    oidc_token {
      service_account_email = google_service_account.backup_scheduler.email
      audience              = var.backup_job_url
    }
  }
}

# Outputs
output "scheduler_service_account_email" {
  description = "Email of the service account used by Cloud Scheduler"
  value       = google_service_account.backup_scheduler.email
}

output "daily_backup_job_name" {
  description = "Name of the daily backup Cloud Scheduler job"
  value       = google_cloud_scheduler_job.daily_backup.name
}

output "weekly_backup_job_name" {
  description = "Name of the weekly backup Cloud Scheduler job"
  value       = google_cloud_scheduler_job.weekly_full_backup.name
}

