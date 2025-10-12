resource "google_project_service" "storage_api" {
  project = var.project_id
  service = "storage.googleapis.com"
}

resource "google_storage_bucket" "frontend" {
  project      = var.project_id
  name         = "${var.project_id}-frontend"
  location     = var.region
  storage_class = "STANDARD"

  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

resource "google_storage_bucket" "uploads" {
  project      = var.project_id
  name         = "${var.project_id}-uploads"
  location     = var.region
  storage_class = "STANDARD"
}

