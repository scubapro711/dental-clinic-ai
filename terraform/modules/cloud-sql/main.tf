resource "google_project_service" "sql_api" {
  project = var.project_id
  service = "sqladmin.googleapis.com"
}

resource "google_sql_database_instance" "main" {
  project          = var.project_id
  name             = "dentaflow-db-instance"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-g1-small"
    ip_configuration {
      ipv4_enabled = true
      private_network = google_compute_network.main.id
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
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

