#!/bin/bash

# AI Dental Clinic Management System - AWS Deployment Script
# This script builds Docker images, pushes them to ECR, and deploys to ECS

set -e

# Configuration
PROJECT_NAME="dental-clinic-ai"
ENVIRONMENT="${ENVIRONMENT:-prod}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if AWS CLI is installed and configured
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials are not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    log_success "All prerequisites are met."
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build Gateway image
    log_info "Building Gateway service image..."
    docker build -f infrastructure/docker/Dockerfile.gateway -t ${PROJECT_NAME}-gateway:latest .
    
    # Build AI Agents image
    log_info "Building AI Agents service image..."
    docker build -f infrastructure/docker/Dockerfile.agents -t ${PROJECT_NAME}-ai-agents:latest .
    
    log_success "Docker images built successfully."
}

# Login to ECR
ecr_login() {
    log_info "Logging in to Amazon ECR..."
    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    log_success "Successfully logged in to ECR."
}

# Create ECR repositories if they don't exist
create_ecr_repositories() {
    log_info "Creating ECR repositories if they don't exist..."
    
    # Create Gateway repository
    aws ecr describe-repositories --repository-names ${PROJECT_NAME}-${ENVIRONMENT}-gateway --region ${AWS_REGION} &> /dev/null || {
        log_info "Creating Gateway ECR repository..."
        aws ecr create-repository --repository-name ${PROJECT_NAME}-${ENVIRONMENT}-gateway --region ${AWS_REGION}
    }
    
    # Create AI Agents repository
    aws ecr describe-repositories --repository-names ${PROJECT_NAME}-${ENVIRONMENT}-ai-agents --region ${AWS_REGION} &> /dev/null || {
        log_info "Creating AI Agents ECR repository..."
        aws ecr create-repository --repository-name ${PROJECT_NAME}-${ENVIRONMENT}-ai-agents --region ${AWS_REGION}
    }
    
    log_success "ECR repositories are ready."
}

# Tag and push images to ECR
push_images() {
    log_info "Tagging and pushing images to ECR..."
    
    # Tag and push Gateway image
    log_info "Pushing Gateway service image..."
    docker tag ${PROJECT_NAME}-gateway:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-gateway:latest
    docker tag ${PROJECT_NAME}-gateway:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-gateway:$(date +%Y%m%d-%H%M%S)
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-gateway:latest
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-gateway:$(date +%Y%m%d-%H%M%S)
    
    # Tag and push AI Agents image
    log_info "Pushing AI Agents service image..."
    docker tag ${PROJECT_NAME}-ai-agents:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-ai-agents:latest
    docker tag ${PROJECT_NAME}-ai-agents:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-ai-agents:$(date +%Y%m%d-%H%M%S)
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-ai-agents:latest
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-${ENVIRONMENT}-ai-agents:$(date +%Y%m%d-%H%M%S)
    
    log_success "Images pushed to ECR successfully."
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd infrastructure/terraform/aws
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init
    
    # Create workspace if it doesn't exist
    terraform workspace select ${ENVIRONMENT} 2>/dev/null || terraform workspace new ${ENVIRONMENT}
    
    # Plan deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var="environment=${ENVIRONMENT}" -var="aws_region=${AWS_REGION}" -out=tfplan
    
    # Apply deployment
    log_info "Applying Terraform deployment..."
    terraform apply tfplan
    
    cd ../../..
    
    log_success "Infrastructure deployed successfully."
}

# Update ECS services
update_ecs_services() {
    log_info "Updating ECS services..."
    
    # Force new deployment for Gateway service
    aws ecs update-service \
        --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster \
        --service ${PROJECT_NAME}-${ENVIRONMENT}-gateway \
        --force-new-deployment \
        --region ${AWS_REGION}
    
    # Force new deployment for AI Agents service
    aws ecs update-service \
        --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster \
        --service ${PROJECT_NAME}-${ENVIRONMENT}-ai-agents \
        --force-new-deployment \
        --region ${AWS_REGION}
    
    log_success "ECS services updated successfully."
}

# Wait for deployment to complete
wait_for_deployment() {
    log_info "Waiting for deployment to complete..."
    
    # Wait for Gateway service
    log_info "Waiting for Gateway service to stabilize..."
    aws ecs wait services-stable \
        --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster \
        --services ${PROJECT_NAME}-${ENVIRONMENT}-gateway \
        --region ${AWS_REGION}
    
    # Wait for AI Agents service
    log_info "Waiting for AI Agents service to stabilize..."
    aws ecs wait services-stable \
        --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster \
        --services ${PROJECT_NAME}-${ENVIRONMENT}-ai-agents \
        --region ${AWS_REGION}
    
    log_success "Deployment completed successfully."
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    # Get load balancer DNS name
    LB_DNS=$(aws elbv2 describe-load-balancers \
        --names ${PROJECT_NAME}-${ENVIRONMENT}-alb \
        --query 'LoadBalancers[0].DNSName' \
        --output text \
        --region ${AWS_REGION})
    
    if [ "$LB_DNS" != "None" ] && [ "$LB_DNS" != "" ]; then
        log_info "Load balancer DNS: $LB_DNS"
        
        # Check Gateway health
        log_info "Checking Gateway service health..."
        for i in {1..30}; do
            if curl -f -s "http://$LB_DNS/health" > /dev/null; then
                log_success "Gateway service is healthy."
                break
            else
                log_warning "Gateway service not ready yet. Attempt $i/30..."
                sleep 10
            fi
        done
        
        # Check AI Agents health
        log_info "Checking AI Agents service health..."
        for i in {1..30}; do
            if curl -f -s "http://$LB_DNS/ai/health" > /dev/null; then
                log_success "AI Agents service is healthy."
                break
            else
                log_warning "AI Agents service not ready yet. Attempt $i/30..."
                sleep 10
            fi
        done
        
        log_success "Application is accessible at: http://$LB_DNS"
    else
        log_warning "Could not retrieve load balancer DNS name."
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f infrastructure/terraform/aws/tfplan
    log_success "Cleanup completed."
}

# Main deployment function
main() {
    log_info "Starting AWS deployment for ${PROJECT_NAME} (${ENVIRONMENT})..."
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    check_prerequisites
    build_images
    ecr_login
    create_ecr_repositories
    push_images
    deploy_infrastructure
    update_ecs_services
    wait_for_deployment
    health_check
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Your application is now running on AWS."
}

# Script usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment    Environment (dev, staging, prod) [default: prod]"
    echo "  -r, --region         AWS region [default: us-east-1]"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  ENVIRONMENT          Environment name"
    echo "  AWS_REGION           AWS region"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy to prod in us-east-1"
    echo "  $0 -e staging -r us-west-2          # Deploy to staging in us-west-2"
    echo "  ENVIRONMENT=dev $0                   # Deploy to dev using environment variable"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run main function
main "$@"
