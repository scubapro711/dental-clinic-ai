resource "google_project_service" "vpc_api" {
  project = var.project_id
  service = "compute.googleapis.com"
}

resource "google_compute_network" "main" {
  project                 = var.project_id
  name                    = "dentaflow-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  project      = var.project_id
  name         = "dentaflow-subnet"
  ip_cidr_range = "10.0.0.0/24"
  network      = google_compute_network.main.id
  region       = var.region
}

resource "google_compute_firewall" "allow_ssh" {
  project = var.project_id
  name    = "allow-ssh"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}

