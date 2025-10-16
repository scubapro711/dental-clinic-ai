# Google Cloud Monitoring Resources for DentaFlow SaaS

# Notification Channels
resource "google_monitoring_notification_channel" "email_alerts" {
  display_name = "Email Alerts"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
  
  enabled = true
}

resource "google_monitoring_notification_channel" "slack_alerts" {
  display_name = "Slack Alerts"
  type         = "slack"
  
  labels = {
    channel_name = "#dentaflow-alerts"
  }
  
  sensitive_labels {
    auth_token = var.slack_webhook_url
  }
  
  enabled = true
}

# Uptime Checks
resource "google_monitoring_uptime_check_config" "api_health" {
  display_name = "DentaFlow API Health Check"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/health"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "api.dentaflow.ai"
    }
  }
}

resource "google_monitoring_uptime_check_config" "frontend_health" {
  display_name = "DentaFlow Frontend Health Check"
  timeout      = "10s"
  period       = "60s"
  
  http_check {
    path         = "/"
    port         = 443
    use_ssl      = true
    validate_ssl = true
  }
  
  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = "dentaflow.ai"
    }
  }
}

# Alert Policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High API Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id,
    google_monitoring_notification_channel.slack_alerts.id
  ]
  
  alert_strategy {
    auto_close = "1800s"
  }
  
  documentation {
    content   = "API error rate has exceeded 5% over the last 5 minutes. Investigate immediately."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "high_response_time" {
  display_name = "High API Response Time"
  combiner     = "OR"
  
  conditions {
    display_name = "Response time > 2s (p95)"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000  # milliseconds
      
      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id
  ]
  
  documentation {
    content   = "API response time has exceeded 2 seconds (p95) over the last 5 minutes."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "high_memory_usage" {
  display_name = "High Memory Usage"
  combiner     = "OR"
  
  conditions {
    display_name = "Memory > 80%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/container/memory/utilizations\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id
  ]
  
  documentation {
    content   = "Cloud Run instance memory usage has exceeded 80% for 5 minutes."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "uptime_check_failure" {
  display_name = "API Health Check Failed"
  combiner     = "OR"
  
  conditions {
    display_name = "Health check failed"
    
    condition_threshold {
      filter          = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND metric.label.check_id=\"${google_monitoring_uptime_check_config.api_health.uptime_check_id}\""
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = 0.9
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_FRACTION_TRUE"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id,
    google_monitoring_notification_channel.slack_alerts.id
  ]
  
  documentation {
    content   = "API health check has failed. Service may be down."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "database_connection_pool" {
  display_name = "Database Connection Pool Near Limit"
  combiner     = "OR"
  
  conditions {
    display_name = "Connection pool > 80%"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 80
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id
  ]
  
  documentation {
    content   = "Database connection pool is >80% utilized. May need to scale."
    mime_type = "text/markdown"
  }
}

resource "google_monitoring_alert_policy" "database_storage" {
  display_name = "Database Storage >80%"
  combiner     = "OR"
  
  conditions {
    display_name = "Storage > 80%"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/disk/utilization\""
      duration        = "600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id
  ]
  
  documentation {
    content   = "Cloud SQL database storage is >80% full. Consider increasing storage."
    mime_type = "text/markdown"
  }
}

# Log-Based Metrics
resource "google_logging_metric" "failed_login_attempts" {
  name   = "failed_login_attempts"
  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.event=\"login_failed\""
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "api_errors" {
  name   = "api_errors"
  filter = "resource.type=\"cloud_run_revision\" AND httpRequest.status>=500"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "slow_queries" {
  name   = "slow_queries"
  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.query_time>1000"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

resource "google_logging_metric" "security_events" {
  name   = "security_events"
  filter = "resource.type=\"cloud_run_revision\" AND (jsonPayload.event=\"unauthorized_access\" OR jsonPayload.event=\"suspicious_activity\")"
  
  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
  }
}

# Alert for Failed Login Attempts
resource "google_monitoring_alert_policy" "high_failed_login_rate" {
  display_name = "High Failed Login Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Failed logins > 10"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"logging.googleapis.com/user/${google_logging_metric.failed_login_attempts.name}\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 10
      
      aggregations {
        alignment_period   = "600s"
        per_series_aligner = "ALIGN_SUM"
      }
    }
  }
  
  notification_channels = [
    google_monitoring_notification_channel.email_alerts.id,
    google_monitoring_notification_channel.slack_alerts.id
  ]
  
  documentation {
    content   = "More than 10 failed login attempts from the same IP in 10 minutes. Possible brute force attack."
    mime_type = "text/markdown"
  }
}

# Variables
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default     = "alerts@dentaflow.ai"
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for alerts"
  type        = string
  sensitive   = true
}

# Outputs
output "notification_channels" {
  description = "Notification channel IDs"
  value = {
    email = google_monitoring_notification_channel.email_alerts.id
    slack = google_monitoring_notification_channel.slack_alerts.id
  }
}

output "uptime_checks" {
  description = "Uptime check IDs"
  value = {
    api      = google_monitoring_uptime_check_config.api_health.uptime_check_id
    frontend = google_monitoring_uptime_check_config.frontend_health.uptime_check_id
  }
}

