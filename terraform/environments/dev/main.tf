terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.28.0"
    }
  }

  required_version = ">= 1.0"
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

module "networking" {
  source = "../../modules/networking"

  project_id = var.gcp_project_id
  region     = var.gcp_region
}

module "cloud_sql" {
  source = "../../modules/cloud-sql"

  project_id = var.gcp_project_id
  region     = var.gcp_region
  db_password = var.db_password
}

module "cloud_run" {
  source = "../../modules/cloud-run"

  project_id        = var.gcp_project_id
  region            = var.gcp_region
  service_name      = "dentaflow-backend-dev"
  image_name        = "gcr.io/${var.gcp_project_id}/dentaflow-backend:latest"
  db_connection_name = module.cloud_sql.instance_connection_name
  db_password_secret = module.cloud_sql.db_password_secret_name
}

