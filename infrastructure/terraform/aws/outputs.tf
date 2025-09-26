# Terraform Outputs
# Important resource information for AI Dental Clinic Management System

# Network Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

# Load Balancer Outputs
output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

# Application URLs
output "application_url" {
  description = "URL to access the application"
  value       = var.certificate_arn != "" ? "https://${aws_lb.main.dns_name}" : "http://${aws_lb.main.dns_name}"
}

output "gateway_target_group_arn" {
  description = "ARN of the Gateway target group"
  value       = aws_lb_target_group.gateway.arn
}

output "ai_agents_target_group_arn" {
  description = "ARN of the AI Agents target group"
  value       = aws_lb_target_group.ai_agents.arn
}

# ECS Outputs
output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.main.arn
}

output "gateway_service_name" {
  description = "Name of the Gateway ECS service"
  value       = aws_ecs_service.gateway.name
}

output "ai_agents_service_name" {
  description = "Name of the AI Agents ECS service"
  value       = aws_ecs_service.ai_agents.name
}

# Database Outputs
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database master username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# Redis Outputs
output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
  sensitive   = true
}

output "redis_port" {
  description = "ElastiCache Redis port"
  value       = aws_elasticache_cluster.redis.port
}

# ECR Outputs
output "gateway_ecr_repository_url" {
  description = "URL of the Gateway ECR repository"
  value       = aws_ecr_repository.gateway.repository_url
}

output "ai_agents_ecr_repository_url" {
  description = "URL of the AI Agents ECR repository"
  value       = aws_ecr_repository.ai_agents.repository_url
}

# Secrets Manager Outputs
output "secrets_kms_key_id" {
  description = "KMS key ID for secrets encryption"
  value       = aws_kms_key.secrets.key_id
}

output "secrets_kms_key_arn" {
  description = "KMS key ARN for secrets encryption"
  value       = aws_kms_key.secrets.arn
}

output "database_credentials_secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.db_credentials.arn
  sensitive   = true
}

output "openai_api_key_secret_arn" {
  description = "ARN of the OpenAI API key secret"
  value       = aws_secretsmanager_secret.openai_api_key.arn
  sensitive   = true
}

output "app_config_secret_arn" {
  description = "ARN of the application configuration secret"
  value       = aws_secretsmanager_secret.app_config.arn
  sensitive   = true
}

# IAM Outputs
output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task.arn
}

# Security Group Outputs
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "ID of the ECS security group"
  value       = aws_security_group.ecs.id
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = aws_security_group.redis.id
}

# Monitoring Outputs
output "sns_alerts_topic_arn" {
  description = "ARN of the SNS alerts topic"
  value       = aws_sns_topic.alerts.arn
}

output "gateway_log_group_name" {
  description = "Name of the Gateway CloudWatch log group"
  value       = aws_cloudwatch_log_group.gateway.name
}

output "ai_agents_log_group_name" {
  description = "Name of the AI Agents CloudWatch log group"
  value       = aws_cloudwatch_log_group.ai_agents.name
}

# Auto Scaling Outputs
output "gateway_autoscaling_target_resource_id" {
  description = "Resource ID of the Gateway auto scaling target"
  value       = var.enable_auto_scaling ? aws_appautoscaling_target.gateway[0].resource_id : null
}

output "ai_agents_autoscaling_target_resource_id" {
  description = "Resource ID of the AI Agents auto scaling target"
  value       = var.enable_auto_scaling ? aws_appautoscaling_target.ai_agents[0].resource_id : null
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "project_name" {
  description = "Project name"
  value       = var.project_name
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

# Deployment Information
output "deployment_timestamp" {
  description = "Timestamp of the deployment"
  value       = timestamp()
}

output "terraform_workspace" {
  description = "Terraform workspace"
  value       = terraform.workspace
}

# Connection Strings (for application configuration)
output "database_connection_string" {
  description = "Database connection string template"
  value       = "mysql://${aws_db_instance.main.username}:PASSWORD@${aws_db_instance.main.endpoint}:${aws_db_instance.main.port}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.port}/0"
  sensitive   = true
}

# Health Check URLs
output "gateway_health_check_url" {
  description = "Gateway service health check URL"
  value       = "${var.certificate_arn != "" ? "https" : "http"}://${aws_lb.main.dns_name}/health"
}

output "ai_agents_health_check_url" {
  description = "AI Agents service health check URL"
  value       = "${var.certificate_arn != "" ? "https" : "http"}://${aws_lb.main.dns_name}/ai/health"
}
