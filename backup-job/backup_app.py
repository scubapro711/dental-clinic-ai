#!/usr/bin/env python3
"""
Database Backup Cloud Run Job
Executes database backups triggered by Cloud Scheduler
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_backup(backup_type="full", retention_days=30, verify_integrity=False):
    """
    Execute database backup script
    
    Args:
        backup_type: Type of backup (full, incremental)
        retention_days: Number of days to retain backup
        verify_integrity: Whether to verify backup integrity
        
    Returns:
        dict: Backup result with status and details
    """
    try:
        logger.info(f"Starting {backup_type} backup...")
        
        # Set environment variables for backup script
        env = os.environ.copy()
        env['BACKUP_TYPE'] = backup_type
        env['RETENTION_DAYS'] = str(retention_days)
        env['VERIFY_INTEGRITY'] = str(verify_integrity).lower()
        
        # Run backup script
        result = subprocess.run(
            ['/app/backup-database-gcs.sh'],
            env=env,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        
        if result.returncode == 0:
            logger.info("Backup completed successfully")
            return {
                'status': 'success',
                'backup_type': backup_type,
                'timestamp': datetime.utcnow().isoformat(),
                'retention_days': retention_days,
                'output': result.stdout
            }
        else:
            logger.error(f"Backup failed: {result.stderr}")
            return {
                'status': 'failed',
                'backup_type': backup_type,
                'timestamp': datetime.utcnow().isoformat(),
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        logger.error("Backup timed out after 30 minutes")
        return {
            'status': 'failed',
            'error': 'Backup timed out after 30 minutes'
        }
    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }

def send_slack_notification(result):
    """Send backup result notification to Slack"""
    try:
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        if not slack_webhook:
            logger.warning("SLACK_WEBHOOK_URL not set, skipping notification")
            return
        
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        message = {
            "text": f"{status_emoji} Database Backup {result['status'].upper()}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Database Backup {result['status'].upper()}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Type:*\n{result.get('backup_type', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Time:*\n{result.get('timestamp', 'N/A')}"},
                        {"type": "mrkdwn", "text": f"*Retention:*\n{result.get('retention_days', 'N/A')} days"},
                        {"type": "mrkdwn", "text": f"*Status:*\n{result['status']}"}
                    ]
                }
            ]
        }
        
        if result['status'] == 'failed':
            message['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:*\n```{result.get('error', 'Unknown error')}```"
                }
            })
        
        import requests
        response = requests.post(slack_webhook, json=message, timeout=10)
        response.raise_for_status()
        logger.info("Slack notification sent successfully")
        
    except Exception as e:
        logger.error(f"Failed to send Slack notification: {str(e)}")

@app.route('/backup', methods=['POST'])
def backup():
    """
    HTTP endpoint for triggering backups
    Expected JSON payload:
    {
        "backup_type": "full",
        "retention_days": 30,
        "notify_slack": true,
        "verify_integrity": false
    }
    """
    try:
        # Parse request data
        data = request.get_json() or {}
        backup_type = data.get('backup_type', 'full')
        retention_days = data.get('retention_days', 30)
        notify_slack = data.get('notify_slack', True)
        verify_integrity = data.get('verify_integrity', False)
        
        logger.info(f"Received backup request: {data}")
        
        # Execute backup
        result = run_backup(
            backup_type=backup_type,
            retention_days=retention_days,
            verify_integrity=verify_integrity
        )
        
        # Send notification if requested
        if notify_slack:
            send_slack_notification(result)
        
        # Return result
        status_code = 200 if result['status'] == 'success' else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Backup endpoint error: {str(e)}")
        return jsonify({
            'status': 'failed',
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

