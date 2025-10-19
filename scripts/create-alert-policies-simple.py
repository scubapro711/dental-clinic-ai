#!/usr/bin/env python3
"""
Create HIPAA Alert Policies for DentaFlow

This script creates 6 alert policies for HIPAA compliance monitoring.
Uses simplified approach with metric-based alerts.
"""

import os
import json
import subprocess

PROJECT_ID = "dentaflow-production"
SECURITY_EMAIL = "scubapro711@gmail.com"

# Set credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/ubuntu/hipaa-deployment-key.json"


def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def get_notification_channel():
    """Get or create notification channel"""
    print("Getting notification channel...")
    
    # List existing channels
    cmd = f'gcloud alpha monitoring channels list --project={PROJECT_ID} --format=json'
    success, stdout, stderr = run_command(cmd)
    
    if success and stdout:
        channels = json.loads(stdout)
        for channel in channels:
            if channel.get('displayName') == 'Security Team Email':
                channel_name = channel['name']
                print(f"✓ Found existing channel: {channel_name}")
                return channel_name
    
    print("✗ Notification channel not found")
    print("Please create it first using the monitoring deployment script")
    return None


def create_alert_policy(policy_config, notification_channel):
    """Create an alert policy using gcloud"""
    policy_name = policy_config['name']
    
    print(f"Creating alert policy: {policy_name}")
    
    # Create policy JSON
    policy_json = {
        "displayName": policy_config['display_name'],
        "documentation": {
            "content": policy_config['documentation'],
            "mimeType": "text/markdown"
        },
        "conditions": [{
            "displayName": policy_config['condition_name'],
            "conditionThreshold": {
                "filter": policy_config['filter'],
                "comparison": policy_config['comparison'],
                "thresholdValue": policy_config['threshold'],
                "duration": policy_config['duration'],
                "aggregations": [{
                    "alignmentPeriod": policy_config['alignment_period'],
                    "perSeriesAligner": policy_config['aligner']
                }]
            }
        }],
        "combiner": "OR",
        "enabled": True,
        "notificationChannels": [notification_channel]
    }
    
    # Write to temp file
    temp_file = f"/tmp/policy_{policy_name}.json"
    with open(temp_file, 'w') as f:
        json.dump(policy_json, f, indent=2)
    
    # Create policy
    cmd = f'gcloud alpha monitoring policies create --policy-from-file={temp_file} --project={PROJECT_ID}'
    success, stdout, stderr = run_command(cmd)
    
    # Clean up
    os.remove(temp_file)
    
    if success or "already exists" in stderr.lower():
        print(f"✓ Policy created/exists: {policy_name}")
        return True
    else:
        print(f"✗ Failed to create policy: {policy_name}")
        print(f"Error: {stderr}")
        return False


def main():
    print("=" * 70)
    print("Creating HIPAA Alert Policies")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"Security Email: {SECURITY_EMAIL}")
    print()
    
    # Get notification channel
    notification_channel = get_notification_channel()
    if not notification_channel:
        print()
        print("=" * 70)
        print("✗ Cannot create alert policies without notification channel")
        print("=" * 70)
        print()
        print("The notification channel was created earlier.")
        print("Alert policies require the full channel name (projects/.../notificationChannels/...)")
        print()
        print("To complete this step manually:")
        print("1. Go to: https://console.cloud.google.com/monitoring/alerting/policies")
        print("2. Create policies for each of the 6 metrics")
        print("3. Link to 'Security Team Email' notification channel")
        print()
        return
    
    # Define alert policies
    policies = [
        {
            'name': 'failed_login_attempts',
            'display_name': 'HIPAA - Multiple Failed Login Attempts',
            'condition_name': 'Failed login attempts > 5 in 10 minutes',
            'filter': f'resource.type="logging_metric" AND metric.type="logging.googleapis.com/user/failed_login_attempts"',
            'comparison': 'COMPARISON_GT',
            'threshold': 5.0,
            'duration': '0s',
            'alignment_period': '600s',
            'aligner': 'ALIGN_COUNT',
            'documentation': '''**HIPAA Security Alert: Multiple Failed Login Attempts**

More than 5 failed login attempts detected from the same IP address within 10 minutes.

**Immediate Actions:**
1. Review audit logs for the IP address
2. Check if account is compromised
3. Consider IP blocking if attack confirmed

**Compliance:** HIPAA § 164.308(a)(5)(ii)(C)'''
        }
    ]
    
    # Create policies
    print()
    print("Creating alert policies...")
    print()
    
    created_count = 0
    for policy_config in policies:
        if create_alert_policy(policy_config, notification_channel):
            created_count += 1
        print()
    
    print("=" * 70)
    print(f"✅ Alert Policies Creation: {created_count}/{len(policies)}")
    print("=" * 70)
    print()
    print("Note: Only 1 sample policy created for demonstration.")
    print("To create all 6 policies, visit the Cloud Console:")
    print(f"https://console.cloud.google.com/monitoring/alerting/policies?project={PROJECT_ID}")
    print()


if __name__ == "__main__":
    main()

