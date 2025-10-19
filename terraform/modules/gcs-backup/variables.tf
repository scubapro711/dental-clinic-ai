# Variables for GCS Backup Module

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "location" {
  description = "GCS bucket location (region or multi-region)"
  type        = string
  default     = "US"
}

variable "environment" {
  description = "Environment name (e.g., production, staging)"
  type        = string
  default     = "production"
}

variable "retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

variable "kms_key_name" {
  description = "KMS key name for encryption (optional)"
  type        = string
  default     = null
}

variable "backup_service_account" {
  description = "Service account email for backup operations"
  type        = string
}

variable "cloudsql_service_account" {
  description = "Cloud SQL service account email"
  type        = string
}

