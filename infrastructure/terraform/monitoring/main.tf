# HIPAA Compliance Alert Policies
# This Terraform configuration creates all required monitoring alert policies

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "dentaflow-production"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "notification_email" {
  description = "Email for security alerts"
  type        = string
  default     = "scubapro711@gmail.com"
}

# Notification Channel
resource "google_monitoring_notification_channel" "security_email" {
  display_name = "Security Team Email"
  type         = "email"
  
  labels = {
    email_address = var.notification_email
  }

  enabled = true
}

# Log-Based Metrics (must exist first)
resource "google_logging_metric" "failed_login_attempts" {
  name   = "hipaa_failed_login_attempts"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="login_failed"
    severity>=ERROR
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "user"
      value_type  = "STRING"
      description = "User attempting login"
    }
  }

  label_extractors = {
    "user" = "EXTRACT(jsonPayload.user)"
  }
}

resource "google_logging_metric" "unauthorized_access" {
  name   = "hipaa_unauthorized_access_attempts"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="unauthorized_access"
    severity>=WARNING
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "resource"
      value_type  = "STRING"
      description = "Resource accessed"
    }
  }

  label_extractors = {
    "resource" = "EXTRACT(jsonPayload.resource)"
  }
}

resource "google_logging_metric" "data_export_events" {
  name   = "hipaa_data_export_events"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="data_export"
    severity>=NOTICE
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "user"
      value_type  = "STRING"
      description = "User exporting data"
    }
  }

  label_extractors = {
    "user" = "EXTRACT(jsonPayload.user)"
  }
}

resource "google_logging_metric" "phi_access_outside_hours" {
  name   = "hipaa_phi_access_outside_hours"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="phi_access"
    jsonPayload.outside_hours=true
    severity>=WARNING
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "user"
      value_type  = "STRING"
      description = "User accessing PHI"
    }
  }

  label_extractors = {
    "user" = "EXTRACT(jsonPayload.user)"
  }
}

resource "google_logging_metric" "bulk_data_operations" {
  name   = "hipaa_bulk_data_operations"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="bulk_operation"
    jsonPayload.record_count>100
    severity>=NOTICE
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "operation_type"
      value_type  = "STRING"
      description = "Type of bulk operation"
    }
  }

  label_extractors = {
    "operation_type" = "EXTRACT(jsonPayload.operation_type)"
  }
}

resource "google_logging_metric" "api_rate_limit_exceeded" {
  name   = "hipaa_api_rate_limit_exceeded"
  filter = <<-EOT
    resource.type="cloud_run_revision"
    jsonPayload.event="rate_limit_exceeded"
    severity>=WARNING
  EOT

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"
    
    labels {
      key         = "client_ip"
      value_type  = "STRING"
      description = "Client IP address"
    }
  }

  label_extractors = {
    "client_ip" = "EXTRACT(jsonPayload.client_ip)"
  }
}

# Alert Policies

# 1. Failed Login Attempts Alert
resource "google_monitoring_alert_policy" "failed_login_alert" {
  display_name = "HIPAA: Failed Login Attempts"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Failed login attempts > 5 in 5 minutes"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.failed_login_attempts.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "Multiple failed login attempts detected. This may indicate a brute force attack. Investigate immediately."
    mime_type = "text/markdown"
  }
}

# 2. Unauthorized Access Alert
resource "google_monitoring_alert_policy" "unauthorized_access_alert" {
  display_name = "HIPAA: Unauthorized Access Attempts"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Unauthorized access attempts detected"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.unauthorized_access.name}\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "Unauthorized access attempt detected. Review user permissions and access logs immediately."
    mime_type = "text/markdown"
  }
}

# 3. Data Export Alert
resource "google_monitoring_alert_policy" "data_export_alert" {
  display_name = "HIPAA: Data Export Events"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Data export event detected"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.data_export_events.name}\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "3600s"
  }

  documentation {
    content   = "PHI data export detected. Verify this is authorized and document in audit log."
    mime_type = "text/markdown"
  }
}

# 4. PHI Access Outside Hours Alert
resource "google_monitoring_alert_policy" "phi_outside_hours_alert" {
  display_name = "HIPAA: PHI Access Outside Business Hours"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "PHI accessed outside business hours"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.phi_access_outside_hours.name}\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "PHI accessed outside normal business hours. Verify this access is authorized."
    mime_type = "text/markdown"
  }
}

# 5. Bulk Data Operations Alert
resource "google_monitoring_alert_policy" "bulk_operations_alert" {
  display_name = "HIPAA: Bulk Data Operations"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "Bulk data operation detected"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.bulk_data_operations.name}\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "3600s"
  }

  documentation {
    content   = "Bulk data operation detected (>100 records). Verify this is authorized and monitor for data exfiltration."
    mime_type = "text/markdown"
  }
}

# 6. API Rate Limit Alert
resource "google_monitoring_alert_policy" "rate_limit_alert" {
  display_name = "HIPAA: API Rate Limit Exceeded"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "API rate limit exceeded"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.api_rate_limit_exceeded.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.security_email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "API rate limit exceeded multiple times. This may indicate a DoS attack or misconfigured client."
    mime_type = "text/markdown"
  }
}

# Outputs
output "notification_channel_id" {
  description = "ID of the notification channel"
  value       = google_monitoring_notification_channel.security_email.id
}

output "alert_policy_ids" {
  description = "IDs of all alert policies"
  value = {
    failed_login        = google_monitoring_alert_policy.failed_login_alert.id
    unauthorized_access = google_monitoring_alert_policy.unauthorized_access_alert.id
    data_export         = google_monitoring_alert_policy.data_export_alert.id
    phi_outside_hours   = google_monitoring_alert_policy.phi_outside_hours_alert.id
    bulk_operations     = google_monitoring_alert_policy.bulk_operations_alert.id
    rate_limit          = google_monitoring_alert_policy.rate_limit_alert.id
  }
}

