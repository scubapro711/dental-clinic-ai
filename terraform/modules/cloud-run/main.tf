resource "google_project_service" "run_api" {
  project = var.project_id
  service = "run.googleapis.com"
}

resource "google_cloud_run_v2_service" "main" {
  project  = var.project_id
  name     = var.service_name
  location = var.region

  template {
    containers {
      image = var.image_name

      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = var.db_password_secret
            version = "latest"
          }
        }
      }
    }

    annotations = {
      "run.googleapis.com/cloudsql-instances" = var.db_connection_name
    }
  }
}

resource "google_cloud_run_service_iam_member" "allow_public" {
  project  = google_cloud_run_v2_service.main.project
  location = google_cloud_run_v2_service.main.location
  service  = google_cloud_run_v2_service.main.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

