# Variables for Cloud Scheduler Module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Scheduler jobs"
  type        = string
  default     = "us-central1"
}

variable "backup_job_url" {
  description = "URL of the Cloud Run job that performs database backups"
  type        = string
}

