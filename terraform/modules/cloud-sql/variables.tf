variable "project_id" {
  description = "The ID of the GCP project."
  type        = string
}

variable "region" {
  description = "The GCP region."
  type        = string
}

variable "db_password" {
  description = "The password for the database."
  type        = string
  sensitive   = true
}

variable "network_id" {
  description = "The ID of the VPC network for private IP"
  type        = string
}

variable "vpc_peering_connection" {
  description = "The VPC peering connection to depend on"
  type        = string
}

