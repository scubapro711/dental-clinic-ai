#!/usr/bin/env python3
"""
Create HIPAA Log-Based Metrics for DentaFlow

This script creates 6 log-based metrics for HIPAA compliance monitoring:
1. failed_login_attempts
2. unauthorized_phi_access
3. bulk_phi_export
4. database_connection_failures
5. encryption_errors
6. high_error_rate
"""

import os
from google.cloud import logging_v2
from google.api_core import exceptions

PROJECT_ID = "dentaflow-production"

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/hipaa-deployment-key.json"


def create_log_metric(client, metric_config):
    """Create a log-based metric"""
    parent = f"projects/{PROJECT_ID}"
    
    try:
        # Check if metric already exists
        metric_name = f"{parent}/metrics/{metric_config['name']}"
        try:
            existing_metric = client.get_log_metric(metric_name=metric_name)
            print(f"✓ Metric '{metric_config['name']}' already exists")
            return existing_metric
        except exceptions.NotFound:
            pass
        
        # Create metric
        metric = logging_v2.LogMetric(
            name=metric_config['name'],
            description=metric_config['description'],
            filter=metric_config['filter'],
            metric_descriptor=logging_v2.MetricDescriptor(
                metric_kind=logging_v2.MetricDescriptor.MetricKind.DELTA,
                value_type=logging_v2.MetricDescriptor.ValueType.INT64
            )
        )
        
        # Add label extractors if provided
        if 'label_extractors' in metric_config:
            metric.label_extractors = metric_config['label_extractors']
        
        created_metric = client.create_log_metric(
            parent=parent,
            metric=metric
        )
        
        print(f"✓ Created metric: {metric_config['name']}")
        return created_metric
        
    except Exception as e:
        print(f"✗ Error creating metric '{metric_config['name']}': {e}")
        return None


def main():
    print("=" * 60)
    print("Creating HIPAA Log-Based Metrics")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print()
    
    # Create client
    client = logging_v2.MetricsServiceV2Client()
    
    # Define metrics
    metrics = [
        {
            'name': 'failed_login_attempts',
            'description': 'Count of failed login attempts',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                jsonPayload.event="login_failed"
            '''.strip(),
            'label_extractors': {
                'ip_address': 'EXTRACT(jsonPayload.ip_address)',
                'user_email': 'EXTRACT(jsonPayload.email)'
            }
        },
        {
            'name': 'unauthorized_phi_access',
            'description': 'Count of unauthorized PHI access attempts',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                jsonPayload.event="unauthorized_access"
                jsonPayload.resource_type="patient"
            '''.strip(),
            'label_extractors': {
                'user_id': 'EXTRACT(jsonPayload.user_id)',
                'patient_id': 'EXTRACT(jsonPayload.patient_id)'
            }
        },
        {
            'name': 'bulk_phi_export',
            'description': 'Count of bulk PHI data exports (>100 records)',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                jsonPayload.event="data_export"
                jsonPayload.resource_type="patient"
                jsonPayload.record_count>100
            '''.strip(),
            'label_extractors': {
                'user_id': 'EXTRACT(jsonPayload.user_id)',
                'record_count': 'EXTRACT(jsonPayload.record_count)'
            }
        },
        {
            'name': 'database_connection_failures',
            'description': 'Count of database connection failures',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                (jsonPayload.error=~".*database.*connection.*" OR
                 jsonPayload.error=~".*could not connect.*" OR
                 severity="ERROR")
            '''.strip()
        },
        {
            'name': 'encryption_errors',
            'description': 'Count of encryption/decryption errors',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                (jsonPayload.error=~".*encryption.*" OR
                 jsonPayload.error=~".*decrypt.*" OR
                 jsonPayload.event="encryption_error")
            '''.strip()
        },
        {
            'name': 'high_error_rate',
            'description': 'Count of 5xx server errors',
            'filter': '''
                resource.type="cloud_run_revision"
                resource.labels.service_name="dentaflow-backend"
                httpRequest.status>=500
            '''.strip(),
            'label_extractors': {
                'status_code': 'EXTRACT(httpRequest.status)',
                'request_url': 'EXTRACT(httpRequest.requestUrl)'
            }
        }
    ]
    
    # Create each metric
    print("Creating metrics...")
    print()
    
    created_count = 0
    for metric_config in metrics:
        print(f"{metrics.index(metric_config) + 1}. {metric_config['name']}")
        result = create_log_metric(client, metric_config)
        if result:
            created_count += 1
        print()
    
    print("=" * 60)
    print(f"✅ Metrics Creation Complete: {created_count}/{len(metrics)}")
    print("=" * 60)
    print()
    print("To view metrics:")
    print(f"  gcloud logging metrics list --project={PROJECT_ID}")
    print()
    print("Next step:")
    print("  Run: python3 scripts/create-alert-policies.py")
    print()


if __name__ == "__main__":
    main()

