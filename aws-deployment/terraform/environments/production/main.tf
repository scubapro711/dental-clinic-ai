# DentalAI Production Infrastructure
# AWS Region: us-east-1
# Environment: Production

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state (recommended for production)
  # backend "s3" {
  #   bucket         = "dentalai-terraform-state"
  #   key            = "production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "dentalai-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "DentalAI"
      Environment = "production"
      ManagedBy   = "Terraform"
      Owner       = "DevOps"
    }
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"
  
  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = slice(data.aws_availability_zones.available.names, 0, 3)
}

# RDS PostgreSQL Module
module "rds" {
  source = "../../modules/rds"
  
  project_name        = var.project_name
  environment         = var.environment
  vpc_id              = module.vpc.vpc_id
  database_subnets    = module.vpc.database_subnets
  app_security_group  = module.ecs.app_security_group_id
  
  db_name             = var.db_name
  db_username         = var.db_username
  db_password         = var.db_password
  db_instance_class   = var.db_instance_class
  db_allocated_storage = var.db_allocated_storage
}

# ElastiCache Redis Module
module "redis" {
  source = "../../modules/redis"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  cache_subnets      = module.vpc.private_subnets
  app_security_group = module.ecs.app_security_group_id
  
  node_type          = var.redis_node_type
  num_cache_nodes    = var.redis_num_nodes
}

# ECS Fargate Module (Backend)
module "ecs" {
  source = "../../modules/ecs"
  
  project_name    = var.project_name
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  public_subnets  = module.vpc.public_subnets
  private_subnets = module.vpc.private_subnets
  
  # Backend configuration
  backend_image       = var.backend_image
  backend_cpu         = var.backend_cpu
  backend_memory      = var.backend_memory
  backend_desired_count = var.backend_desired_count
  
  # Environment variables
  database_url    = module.rds.connection_string
  redis_url       = module.redis.connection_string
  openai_api_key  = var.openai_api_key
  odoo_url        = var.odoo_url
  odoo_db         = var.odoo_db
  odoo_username   = var.odoo_username
  odoo_password   = var.odoo_password
  use_mock_odoo   = var.use_mock_odoo
}

# S3 + CloudFront Module (Frontend)
module "s3_cloudfront" {
  source = "../../modules/s3-cloudfront"
  
  project_name = var.project_name
  environment  = var.environment
  domain_name  = var.domain_name
  
  # Backend API URL for CORS
  backend_url = module.ecs.alb_dns_name
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "RDS endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "backend_url" {
  description = "Backend API URL"
  value       = "https://${module.ecs.alb_dns_name}"
}

output "frontend_url" {
  description = "Frontend CloudFront URL"
  value       = module.s3_cloudfront.cloudfront_domain_name
}

output "frontend_bucket" {
  description = "Frontend S3 bucket name"
  value       = module.s3_cloudfront.bucket_name
}
