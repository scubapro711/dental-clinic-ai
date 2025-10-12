resource "google_project_service" "sql_api" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
}

resource "google_sql_database_instance" "main" {
  project          = var.project_id
  name             = "dentaflow-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = true

  # Wait for VPC peering to be ready
  depends_on = [var.vpc_peering_connection]

  settings {
    tier = "db-g1-small"
    disk_type = "PD_SSD"
    ip_configuration {
      ipv4_enabled = true
      private_network = var.network_id
    }
  }
}

resource "google_sql_database" "main" {
  project  = var.project_id
  instance = google_sql_database_instance.main.name
  name     = "dentaflow"
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "google_secret_manager_secret" "db_password" {
  project = var.project_id
  secret_id = "db-password"

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

