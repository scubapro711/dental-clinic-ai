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


# ============================================================================
# HIPAA Compliance Alert Policies
# ============================================================================

# Alert Policy 1: Unauthorized PHI Access
resource "google_monitoring_alert_policy" "unauthorized_phi_access" {
  project      = var.project_id
  display_name = "HIPAA: Unauthorized PHI Access Detected"
  combiner     = "OR"

  conditions {
    display_name = "Unauthorized PHI access attempts detected"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/phi_access_unauthorized\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0  # Alert on any unauthorized access

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.user_id", "metric.label.organization_id"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "86400s"  # Auto-close after 24 hours
  }

  documentation {
    content   = "CRITICAL: Unauthorized PHI access attempt detected. This may indicate a security breach or misconfigured access controls. Immediate investigation required."
    mime_type = "text/markdown"
  }

  severity = "CRITICAL"
}

# Alert Policy 2: Multiple Failed Login Attempts
resource "google_monitoring_alert_policy" "failed_login_attempts" {
  project      = var.project_id
  display_name = "HIPAA: Multiple Failed Login Attempts"
  combiner     = "OR"

  conditions {
    display_name = "More than 5 failed login attempts in 5 minutes"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/login_failures\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.user_id", "metric.label.ip_address"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "3600s"  # Auto-close after 1 hour
  }

  documentation {
    content   = "WARNING: Multiple failed login attempts detected. This may indicate a brute-force attack or compromised credentials. Review user account and IP address."
    mime_type = "text/markdown"
  }

  severity = "WARNING"
}

# Alert Policy 3: Encryption Failures
resource "google_monitoring_alert_policy" "encryption_failures" {
  project      = var.project_id
  display_name = "HIPAA: Encryption Operation Failures"
  combiner     = "OR"

  conditions {
    display_name = "Encryption failures detected"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/encryption_failures\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0  # Alert on any encryption failure

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.encryption_type", "metric.label.algorithm"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "3600s"  # Auto-close after 1 hour
  }

  documentation {
    content   = "ERROR: Encryption operation failed. This may compromise data security. Investigate encryption configuration and key management."
    mime_type = "text/markdown"
  }

  severity = "ERROR"
}

# Alert Policy 4: Security Breach Incidents
resource "google_monitoring_alert_policy" "breach_incidents" {
  project      = var.project_id
  display_name = "HIPAA: Security Breach Incident Detected"
  combiner     = "OR"

  conditions {
    display_name = "Security breach incident reported"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/breach_incidents\""
      duration        = "0s"  # Alert immediately
      comparison      = "COMPARISON_GT"
      threshold_value = 0  # Alert on any breach

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.breach_type", "metric.label.organization_id"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "604800s"  # Auto-close after 7 days (requires manual review)
  }

  documentation {
    content   = "🚨 CRITICAL: Security breach incident detected! Immediate action required:\n1. Isolate affected systems\n2. Notify security team\n3. Begin incident response protocol\n4. Document all actions\n5. Prepare breach notification if required by HIPAA"
    mime_type = "text/markdown"
  }

  severity = "CRITICAL"
}

# Alert Policy 5: Expired BAA Agreements
resource "google_monitoring_alert_policy" "expired_baa" {
  project      = var.project_id
  display_name = "HIPAA: Expired BAA Agreement Detected"
  combiner     = "OR"

  conditions {
    display_name = "BAA agreement expired"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/baa_expired_count\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0  # Alert on any expired BAA

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MAX"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.vendor_type", "metric.label.organization_id"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "86400s"  # Auto-close after 24 hours
  }

  documentation {
    content   = "WARNING: BAA (Business Associate Agreement) has expired. This is a HIPAA compliance violation. Renew BAA immediately or cease data sharing with vendor."
    mime_type = "text/markdown"
  }

  severity = "WARNING"
}

# Alert Policy 6: High Volume PHI Access (Potential Data Exfiltration)
resource "google_monitoring_alert_policy" "high_volume_phi_access" {
  project      = var.project_id
  display_name = "HIPAA: High Volume PHI Access Detected"
  combiner     = "OR"

  conditions {
    display_name = "More than 100 PHI access events in 10 minutes"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"custom.googleapis.com/dentaflow/hipaa/phi_access\""
      duration        = "600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 100

      aggregations {
        alignment_period     = "600s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields      = ["metric.label.user_id", "metric.label.organization_id"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "3600s"  # Auto-close after 1 hour
  }

  documentation {
    content   = "WARNING: Unusually high volume of PHI access detected. This may indicate:\n- Legitimate bulk operations (e.g., report generation)\n- Data exfiltration attempt\n- Misconfigured application\n\nInvestigate user activity and verify legitimacy."
    mime_type = "text/markdown"
  }

  severity = "WARNING"
}

