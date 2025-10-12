output "network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.main.id
}

output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.main.name
}

output "subnet_id" {
  description = "The ID of the subnet"
  value       = google_compute_subnetwork.main.id
}

output "vpc_peering_connection" {
  description = "The VPC peering connection for service networking"
  value       = google_service_networking_connection.private_vpc_connection.id
}

