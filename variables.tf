variable "gcp_project_id" {
  description = "The GCP project ID to deploy to."
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy to."
  type        = string
  default     = "us-central1"
}

variable "db_password" {
  description = "The password for the Cloud SQL database."
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "The environment name (dev, staging, production)."
  type        = string
  default     = "staging"
}

