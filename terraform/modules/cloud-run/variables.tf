variable "project_id" {
  description = "The ID of the GCP project."
  type        = string
}

variable "region" {
  description = "The GCP region."
  type        = string
}

variable "service_name" {
  description = "The name of the Cloud Run service."
  type        = string
}

variable "image_name" {
  description = "The name of the container image to deploy."
  type        = string
}

variable "db_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  type        = string
}

variable "db_password_secret" {
  description = "The name of the secret containing the database password."
  type        = string
}

