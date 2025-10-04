# Project Configuration
variable "project_name" {
  description = "Project name"
  type        = string
  default     = "dentalai"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# Network Configuration
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# Database Configuration
variable "db_name" {
  description = "Database name"
  type        = string
  default     = "dentalai"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "dentalai"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 100
}

# Redis Configuration
variable "redis_node_type" {
  description = "Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1
}

# Backend Configuration
variable "backend_image" {
  description = "Backend Docker image"
  type        = string
}

variable "backend_cpu" {
  description = "Backend CPU units"
  type        = number
  default     = 1024
}

variable "backend_memory" {
  description = "Backend memory (MB)"
  type        = number
  default     = 2048
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

# Odoo Configuration
variable "odoo_url" {
  description = "Odoo URL"
  type        = string
  default     = "http://odoo:8069"
}

variable "odoo_db" {
  description = "Odoo database name"
  type        = string
  default     = "dentalai_odoo"
}

variable "odoo_username" {
  description = "Odoo username"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "odoo_password" {
  description = "Odoo password"
  type        = string
  sensitive   = true
}

variable "use_mock_odoo" {
  description = "Use mock Odoo (true) or real Odoo (false)"
  type        = bool
  default     = true
}

# LLM Configuration
variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

# Domain Configuration
variable "domain_name" {
  description = "Custom domain name (optional)"
  type        = string
  default     = ""
}
