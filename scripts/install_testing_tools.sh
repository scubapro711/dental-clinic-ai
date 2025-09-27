#!/bin/bash
# 🔧 Installation Script for Advanced Testing Tools
# מתקין כלי בדיקות מתקדמים לבדיקת תשתיות AWS

set -e

echo "🚀 Installing Advanced Testing Tools for AWS Infrastructure"
echo "=========================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -y

# Install Python dependencies
echo "🐍 Installing Python testing dependencies..."
pip3 install --upgrade pip
pip3 install -r - << EOF
aiohttp>=3.8.0
boto3>=1.26.0
psutil>=5.9.0
requests>=2.28.0
pyyaml>=6.0
asyncio-mqtt>=0.11.0
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-benchmark>=4.0.0
locust>=2.14.0
k6>=0.1.0
chaos-toolkit>=1.14.0
chaos-toolkit-aws>=0.21.0
litmus-sdk>=1.0.0
EOF

# Install K6 (Load Testing)
echo "⚡ Installing K6 Load Testing Tool..."
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6 -y

# Install Locust (Load Testing)
echo "🦗 Installing Locust Load Testing Tool..."
pip3 install locust

# Install Chaos Toolkit
echo "🌪️ Installing Chaos Toolkit..."
pip3 install chaostoolkit chaostoolkit-aws chaostoolkit-kubernetes

# Install AWS CLI v2 (if not already installed)
echo "☁️ Checking AWS CLI..."
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI v2..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

# Install kubectl (for Kubernetes chaos testing)
echo "⚙️ Installing kubectl..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# Install Helm (for LitmusChaos)
echo "⛵ Installing Helm..."
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm -y

# Install Docker Compose (for local testing)
echo "🐳 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional monitoring tools
echo "📊 Installing monitoring tools..."
pip3 install prometheus-client grafana-api

# Install security testing tools
echo "🔒 Installing security testing tools..."
pip3 install bandit safety sqlmap-python

# Install network testing tools
echo "🌐 Installing network testing tools..."
sudo apt-get install -y nmap netcat-openbsd tcpdump wireshark-common

# Create testing directories
echo "📁 Creating testing directories..."
mkdir -p /tmp/testing-results
mkdir -p /tmp/chaos-experiments
mkdir -p /tmp/load-test-results

# Create K6 load test script
echo "📝 Creating K6 load test script..."
cat > /tmp/k6-load-test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up
    { duration: '5m', target: 50 }, // Stay at 50 users
    { duration: '2m', target: 100 }, // Ramp up to 100 users
    { duration: '5m', target: 100 }, // Stay at 100 users
    { duration: '2m', target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.05'], // Error rate should be less than 5%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://dental-prod-alb-230896070.us-east-1.elb.amazonaws.com';

export default function() {
  // Test health endpoint
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Test AI health endpoint
  let aiHealthResponse = http.get(`${BASE_URL}/ai/health`);
  check(aiHealthResponse, {
    'ai health status is 200': (r) => r.status === 200,
  });
  
  // Record errors
  errorRate.add(healthResponse.status !== 200);
  
  sleep(1);
}
EOF

# Create Locust load test script
echo "🦗 Creating Locust load test script..."
cat > /tmp/locustfile.py << 'EOF'
from locust import HttpUser, task, between
import random

class DentalClinicUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        pass
    
    @task(3)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
    
    @task(2)
    def ai_health_check(self):
        """Test AI health endpoint"""
        self.client.get("/ai/health")
    
    @task(1)
    def root_endpoint(self):
        """Test root endpoint"""
        self.client.get("/")
    
    @task(1)
    def docs_endpoint(self):
        """Test docs endpoint"""
        self.client.get("/docs")
EOF

# Create Chaos Toolkit experiment
echo "🌪️ Creating Chaos Toolkit experiment..."
cat > /tmp/chaos-experiments/ecs-task-killer.json << 'EOF'
{
  "version": "1.0.0",
  "title": "ECS Task Resilience Test",
  "description": "Test system resilience by randomly stopping ECS tasks",
  "tags": ["aws", "ecs", "resilience"],
  "configuration": {
    "aws_region": "us-east-1"
  },
  "steady-state-hypothesis": {
    "title": "Application is healthy",
    "probes": [
      {
        "name": "application-must-respond",
        "type": "probe",
        "tolerance": 200,
        "provider": {
          "type": "http",
          "url": "http://dental-prod-alb-230896070.us-east-1.elb.amazonaws.com/health",
          "timeout": 10
        }
      }
    ]
  },
  "method": [
    {
      "name": "stop-random-ecs-task",
      "type": "action",
      "provider": {
        "type": "python",
        "module": "chaosaws.ecs.actions",
        "func": "stop_task",
        "arguments": {
          "cluster": "dental-clinic-cluster",
          "task_arn": null,
          "reason": "Chaos Engineering Test"
        }
      }
    }
  ],
  "rollbacks": []
}
EOF

# Create comprehensive test runner script
echo "🏃 Creating comprehensive test runner..."
cat > /tmp/run-comprehensive-tests.sh << 'EOF'
#!/bin/bash
# Comprehensive Testing Runner

BASE_URL="http://dental-prod-alb-230896070.us-east-1.elb.amazonaws.com"
RESULTS_DIR="/tmp/testing-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting Comprehensive Testing Suite - $TIMESTAMP"
echo "=================================================="

# Create results directory
mkdir -p "$RESULTS_DIR/$TIMESTAMP"

# 1. Run Python Aggressive Testing Suite
echo "🐍 Running Python Aggressive Testing Suite..."
cd /home/ubuntu/dental-clinic-ai
python3 tests/aggressive_deployment_testing_suite.py > "$RESULTS_DIR/$TIMESTAMP/python_tests.log" 2>&1

# 2. Run K6 Load Tests
echo "⚡ Running K6 Load Tests..."
k6 run --env BASE_URL="$BASE_URL" /tmp/k6-load-test.js --out json="$RESULTS_DIR/$TIMESTAMP/k6_results.json"

# 3. Run Locust Load Tests (background)
echo "🦗 Starting Locust Load Tests..."
locust -f /tmp/locustfile.py --host="$BASE_URL" --users 50 --spawn-rate 5 --run-time 300s --html "$RESULTS_DIR/$TIMESTAMP/locust_report.html" --csv "$RESULTS_DIR/$TIMESTAMP/locust" &
LOCUST_PID=$!

# 4. Run Security Tests
echo "🔒 Running Security Tests..."
# Nmap scan
nmap -sV -sC $(echo "$BASE_URL" | sed 's|http://||' | cut -d: -f1) > "$RESULTS_DIR/$TIMESTAMP/nmap_scan.txt" 2>&1

# 5. Run AWS Infrastructure Validation
echo "☁️ Running AWS Infrastructure Validation..."
aws ecs describe-clusters --clusters dental-clinic-cluster > "$RESULTS_DIR/$TIMESTAMP/ecs_cluster_status.json" 2>&1
aws elbv2 describe-load-balancers --names dental-prod-alb > "$RESULTS_DIR/$TIMESTAMP/alb_status.json" 2>&1
aws rds describe-db-instances > "$RESULTS_DIR/$TIMESTAMP/rds_status.json" 2>&1

# 6. Wait for Locust to finish
echo "⏳ Waiting for Locust tests to complete..."
wait $LOCUST_PID

# 7. Generate summary report
echo "📊 Generating summary report..."
cat > "$RESULTS_DIR/$TIMESTAMP/summary.md" << SUMMARY
# Comprehensive Testing Report - $TIMESTAMP

## Test Results Summary

### 1. Python Aggressive Testing Suite
- Location: python_tests.log
- Tests: Infrastructure, Load, Security, Monitoring

### 2. K6 Load Testing
- Location: k6_results.json
- Test: Progressive load from 10 to 100 users

### 3. Locust Load Testing
- Location: locust_report.html, locust_*.csv
- Test: 50 concurrent users for 5 minutes

### 4. Security Testing
- Location: nmap_scan.txt
- Test: Network security scan

### 5. AWS Infrastructure Validation
- Locations: *_status.json files
- Test: AWS services health check

## Next Steps
1. Review all test results
2. Address any failures or warnings
3. Optimize performance based on load test results
4. Implement security recommendations

Generated at: $(date)
SUMMARY

echo "✅ Comprehensive testing completed!"
echo "📁 Results saved to: $RESULTS_DIR/$TIMESTAMP"
echo "📊 View summary: $RESULTS_DIR/$TIMESTAMP/summary.md"
EOF

chmod +x /tmp/run-comprehensive-tests.sh

# Create monitoring dashboard setup
echo "📊 Creating monitoring dashboard setup..."
cat > /tmp/setup-monitoring.py << 'EOF'
#!/usr/bin/env python3
"""
Setup monitoring dashboard for the dental clinic AI system
"""

import boto3
import json

def create_cloudwatch_dashboard():
    """Create CloudWatch dashboard"""
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    
    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/ECS", "CPUUtilization", "ServiceName", "dental-prod-gateway"],
                        ["AWS/ECS", "MemoryUtilization", "ServiceName", "dental-prod-gateway"],
                        ["AWS/ECS", "CPUUtilization", "ServiceName", "dental-prod-ai-agents"],
                        ["AWS/ECS", "MemoryUtilization", "ServiceName", "dental-prod-ai-agents"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "ECS Service Metrics"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/dental-prod-alb/*"],
                        ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/dental-prod-alb/*"],
                        ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", "app/dental-prod-alb/*"],
                        ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", "app/dental-prod-alb/*"],
                        ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", "app/dental-prod-alb/*"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Load Balancer Metrics"
                }
            },
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "dental-prod-database"],
                        ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "dental-prod-database"],
                        ["AWS/RDS", "FreeableMemory", "DBInstanceIdentifier", "dental-prod-database"]
                    ],
                    "period": 300,
                    "stat": "Average",
                    "region": "us-east-1",
                    "title": "RDS Metrics"
                }
            }
        ]
    }
    
    try:
        response = cloudwatch.put_dashboard(
            DashboardName='DentalClinicAI-Production',
            DashboardBody=json.dumps(dashboard_body)
        )
        print(f"✅ Dashboard created: {response}")
    except Exception as e:
        print(f"❌ Failed to create dashboard: {e}")

if __name__ == "__main__":
    create_cloudwatch_dashboard()
EOF

chmod +x /tmp/setup-monitoring.py

echo ""
echo "✅ Installation completed successfully!"
echo "========================================="
echo ""
echo "🔧 Available Testing Tools:"
echo "  • Python Aggressive Testing Suite: /home/ubuntu/dental-clinic-ai/tests/aggressive_deployment_testing_suite.py"
echo "  • K6 Load Testing: k6 run /tmp/k6-load-test.js"
echo "  • Locust Load Testing: locust -f /tmp/locustfile.py"
echo "  • Chaos Toolkit: chaos run /tmp/chaos-experiments/ecs-task-killer.json"
echo "  • Comprehensive Test Runner: /tmp/run-comprehensive-tests.sh"
echo ""
echo "📊 Monitoring:"
echo "  • Setup CloudWatch Dashboard: python3 /tmp/setup-monitoring.py"
echo ""
echo "🚀 Quick Start:"
echo "  1. Run comprehensive tests: bash /tmp/run-comprehensive-tests.sh"
echo "  2. Setup monitoring: python3 /tmp/setup-monitoring.py"
echo "  3. View results in /tmp/testing-results/"
echo ""
echo "📚 Documentation:"
echo "  • K6: https://k6.io/docs/"
echo "  • Locust: https://docs.locust.io/"
echo "  • Chaos Toolkit: https://chaostoolkit.org/"
echo "  • LitmusChaos: https://litmuschaos.io/"
echo ""
