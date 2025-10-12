output "instance_connection_name" {
  description = "The connection name of the Cloud SQL instance."
  value       = google_sql_database_instance.main.connection_name
}

output "db_password_secret_name" {
  description = "The name of the secret containing the database password."
  value       = google_secret_manager_secret.db_password.secret_id
}

