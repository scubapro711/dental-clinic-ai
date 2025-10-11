resource "google_project_service" "monitoring_api" {
  project = var.project_id
  service = "monitoring.googleapis.com"
}

resource "google_monitoring_alert_policy" "high_error_rate" {
  project      = var.project_id
  display_name = "High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5% on Cloud Run"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

resource "google_monitoring_notification_channel" "email" {
  project      = var.project_id
  display_name = "Email Notifications"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

