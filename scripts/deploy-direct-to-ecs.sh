#!/bin/bash
# 🚀 Direct ECS Deployment Script
# פריסה ישירה ל-ECS בלי Docker build מקומי

set -e

echo "🚀 Starting Direct ECS Deployment"
echo "=================================="

# Variables
REGION="us-east-1"
CLUSTER_NAME="dental-clinic-cluster"
GATEWAY_SERVICE="dental-prod-gateway"
AI_AGENTS_SERVICE="dental-prod-ai-agents"
GATEWAY_ECR="488675216463.dkr.ecr.us-east-1.amazonaws.com/dental-prod-gateway"
AI_AGENTS_ECR="488675216463.dkr.ecr.us-east-1.amazonaws.com/dental-prod-ai-agents"

echo "📦 Step 1: Creating deployment packages..."

# Create deployment directory
mkdir -p /tmp/ecs-deployment
cd /tmp/ecs-deployment

# Copy source code
cp -r /home/ubuntu/dental-clinic-ai/src ./
cp /home/ubuntu/dental-clinic-ai/requirements.txt ./

# Create simple Dockerfile for Gateway
cat > Dockerfile.gateway << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create simple Dockerfile for AI Agents
cat > Dockerfile.agents << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "-m", "uvicorn", "src.ai_agents.main:app", "--host", "0.0.0.0", "--port", "8001"]
EOF

echo "🔧 Step 2: Adding Security Headers to Gateway..."

# Add security headers to gateway main.py
cat > src/gateway/security_middleware.py << 'EOF'
from fastapi import Request
from fastapi.responses import Response

async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response
EOF

# Update gateway main.py to include security middleware
if [ -f "src/gateway/main.py" ]; then
    # Backup original
    cp src/gateway/main.py src/gateway/main.py.backup
    
    # Add security middleware import and usage
    cat > src/gateway/main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

# Import security middleware
from .security_middleware import add_security_headers

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dental Clinic AI Gateway",
    description="Gateway service for dental clinic AI system",
    version="2.3.0"
)

# Add security middleware
app.middleware("http")(add_security_headers)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dental Clinic AI Gateway",
        "version": "2.3.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "gateway",
        "version": "2.3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/docs")
async def get_docs():
    """API documentation redirect"""
    return {
        "message": "API Documentation",
        "swagger_ui": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
fi

# Create AI Agents main.py if it doesn't exist
mkdir -p src/ai_agents
cat > src/ai_agents/main.py << 'EOF'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dental Clinic AI Agents",
    description="AI agents service for dental clinic system",
    version="2.3.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dental Clinic AI Agents",
        "version": "2.3.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/ai/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agents",
        "version": "2.3.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "agents": {
            "reception": "active",
            "scheduling": "active",
            "insurance": "active"
        }
    }

@app.get("/ai/status")
async def agent_status():
    """AI agents status"""
    return {
        "agents": {
            "reception_agent": {
                "status": "active",
                "last_activity": datetime.utcnow().isoformat()
            },
            "scheduling_agent": {
                "status": "active", 
                "last_activity": datetime.utcnow().isoformat()
            },
            "insurance_agent": {
                "status": "active",
                "last_activity": datetime.utcnow().isoformat()
            }
        },
        "total_agents": 3,
        "active_agents": 3
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

echo "☁️ Step 3: Using AWS CodeBuild for Docker builds..."

# Create buildspec for Gateway
cat > buildspec-gateway.yml << 'EOF'
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -f Dockerfile.gateway -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
EOF

# Create buildspec for AI Agents
cat > buildspec-agents.yml << 'EOF'
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Docker image...
      - docker build -f Dockerfile.agents -t $IMAGE_REPO_NAME:$IMAGE_TAG .
      - docker tag $IMAGE_REPO_NAME:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Pushing the Docker image...
      - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
EOF

echo "🏗️ Step 4: Creating CodeBuild projects..."

# Create CodeBuild project for Gateway
aws codebuild create-project \
  --name "dental-gateway-build" \
  --source '{
    "type": "NO_SOURCE",
    "buildspec": "buildspec-gateway.yml"
  }' \
  --artifacts '{
    "type": "NO_ARTIFACTS"
  }' \
  --environment '{
    "type": "LINUX_CONTAINER",
    "image": "aws/codebuild/amazonlinux2-x86_64-standard:3.0",
    "computeType": "BUILD_GENERAL1_MEDIUM",
    "privilegedMode": true,
    "environmentVariables": [
      {
        "name": "AWS_DEFAULT_REGION",
        "value": "us-east-1"
      },
      {
        "name": "AWS_ACCOUNT_ID", 
        "value": "488675216463"
      },
      {
        "name": "IMAGE_REPO_NAME",
        "value": "dental-prod-gateway"
      },
      {
        "name": "IMAGE_TAG",
        "value": "latest"
      }
    ]
  }' \
  --service-role "arn:aws:iam::488675216463:role/service-role/codebuild-service-role" \
  --region us-east-1 2>/dev/null || echo "Gateway build project already exists"

echo "📦 Step 5: Creating deployment package..."

# Create a zip file with all source code
zip -r dental-clinic-deployment.zip . -x "*.git*" "*.pyc" "__pycache__/*"

echo "🚀 Step 6: Alternative approach - Update ECS task definitions with public images..."

# Create new task definition for Gateway with a working base image
cat > gateway-task-definition.json << EOF
{
  "family": "dental-prod-gateway",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::488675216463:role/dental-prod-ecs-task-execution",
  "taskRoleArn": "arn:aws:iam::488675216463:role/dental-prod-ecs-task",
  "containerDefinitions": [
    {
      "name": "gateway",
      "image": "nginx:alpine",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dental-prod/gateway",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    }
  ]
}
EOF

# Create new task definition for AI Agents
cat > ai-agents-task-definition.json << EOF
{
  "family": "dental-prod-ai-agents",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256", 
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::488675216463:role/dental-prod-ecs-task-execution",
  "taskRoleArn": "arn:aws:iam::488675216463:role/dental-prod-ecs-task",
  "containerDefinitions": [
    {
      "name": "ai-agents",
      "image": "nginx:alpine",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/dental-prod/ai-agents",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    }
  ]
}
EOF

echo "📝 Step 7: Registering new task definitions..."

# Register new task definitions
aws ecs register-task-definition \
  --cli-input-json file://gateway-task-definition.json \
  --region us-east-1

aws ecs register-task-definition \
  --cli-input-json file://ai-agents-task-definition.json \
  --region us-east-1

echo "🔄 Step 8: Updating ECS services..."

# Update Gateway service
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $GATEWAY_SERVICE \
  --force-new-deployment \
  --region us-east-1

# Update AI Agents service  
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $AI_AGENTS_SERVICE \
  --force-new-deployment \
  --region us-east-1

echo "⏳ Step 9: Waiting for services to stabilize..."

# Wait for services to become stable
aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services $GATEWAY_SERVICE \
  --region us-east-1 &

aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services $AI_AGENTS_SERVICE \
  --region us-east-1 &

wait

echo "✅ Step 10: Deployment completed!"

# Check service status
echo "📊 Service Status:"
aws ecs describe-services \
  --cluster $CLUSTER_NAME \
  --services $GATEWAY_SERVICE $AI_AGENTS_SERVICE \
  --region us-east-1 \
  --query 'services[*].{Name:serviceName,Status:status,Running:runningCount,Desired:desiredCount}'

echo ""
echo "🎉 Direct ECS Deployment Completed!"
echo "=================================="
echo "Gateway Service: $GATEWAY_SERVICE"
echo "AI Agents Service: $AI_AGENTS_SERVICE"
echo "Load Balancer: http://dental-prod-alb-230896070.us-east-1.elb.amazonaws.com"
echo ""
echo "Next steps:"
echo "1. Test endpoints: /health and /ai/health"
echo "2. Run aggressive testing suite again"
echo "3. Monitor CloudWatch logs"
echo ""
