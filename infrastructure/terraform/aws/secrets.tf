# AWS Secrets Manager Configuration
# Secure storage for application secrets and API keys

# KMS Key for encrypting secrets
resource "aws_kms_key" "secrets" {
  description             = "KMS key for encrypting application secrets"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-secrets-key"
  })
}

resource "aws_kms_alias" "secrets" {
  name          = "alias/${local.name_prefix}-secrets"
  target_key_id = aws_kms_key.secrets.key_id
}

# Database credentials secret
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${local.name_prefix}/database/credentials"
  description             = "Database master credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-db-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password != "" ? var.db_password : random_password.db_password.result
  })
}

# Generate random password for database if not provided
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# OpenAI API Key secret
resource "aws_secretsmanager_secret" "openai_api_key" {
  name                    = "${local.name_prefix}/openai/api-key"
  description             = "OpenAI API key for AI services"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-openai-key"
  })
}

resource "aws_secretsmanager_secret_version" "openai_api_key" {
  secret_id = aws_secretsmanager_secret.openai_api_key.id
  secret_string = jsonencode({
    api_key = var.openai_api_key
  })
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}

# Google API credentials secret
resource "aws_secretsmanager_secret" "google_credentials" {
  name                    = "${local.name_prefix}/google/credentials"
  description             = "Google API credentials for various Google services"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-google-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "google_credentials" {
  secret_id = aws_secretsmanager_secret.google_credentials.id
  secret_string = jsonencode({
    api_key                = var.google_api_key
    service_account_key    = var.google_service_account_key
    project_id            = var.google_project_id
    client_id             = var.google_client_id
    client_secret         = var.google_client_secret
    maps_api_key          = var.google_maps_api_key
    translate_api_key     = var.google_translate_api_key
    speech_api_key        = var.google_speech_api_key
  })
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}

# WhatsApp webhook credentials
resource "aws_secretsmanager_secret" "whatsapp_credentials" {
  name                    = "${local.name_prefix}/whatsapp/credentials"
  description             = "WhatsApp webhook credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-whatsapp-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "whatsapp_credentials" {
  secret_id = aws_secretsmanager_secret.whatsapp_credentials.id
  secret_string = jsonencode({
    webhook_token    = var.whatsapp_webhook_token
    verify_token     = random_password.whatsapp_verify_token.result
    app_secret       = random_password.whatsapp_app_secret.result
  })
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "random_password" "whatsapp_verify_token" {
  length  = 32
  special = false
}

resource "random_password" "whatsapp_app_secret" {
  length  = 32
  special = true
}

# Telegram bot credentials
resource "aws_secretsmanager_secret" "telegram_credentials" {
  name                    = "${local.name_prefix}/telegram/credentials"
  description             = "Telegram bot credentials"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-telegram-credentials"
  })
}

resource "aws_secretsmanager_secret_version" "telegram_credentials" {
  secret_id = aws_secretsmanager_secret.telegram_credentials.id
  secret_string = jsonencode({
    bot_token    = var.telegram_bot_token
    webhook_secret = random_password.telegram_webhook_secret.result
  })
  
  lifecycle {
    ignore_changes = [secret_string]
  }
}

resource "random_password" "telegram_webhook_secret" {
  length  = 32
  special = true
}

# Application configuration secrets
resource "aws_secretsmanager_secret" "app_config" {
  name                    = "${local.name_prefix}/app/config"
  description             = "Application configuration secrets"
  kms_key_id              = aws_kms_key.secrets.arn
  recovery_window_in_days = 7
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-app-config"
  })
}

resource "aws_secretsmanager_secret_version" "app_config" {
  secret_id = aws_secretsmanager_secret.app_config.id
  secret_string = jsonencode({
    jwt_secret_key     = random_password.jwt_secret.result
    encryption_key     = random_password.encryption_key.result
    session_secret     = random_password.session_secret.result
    webhook_secret     = random_password.webhook_secret.result
  })
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

resource "random_password" "session_secret" {
  length  = 32
  special = true
}

resource "random_password" "webhook_secret" {
  length  = 32
  special = true
}

# IAM role for ECS tasks to access secrets
resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-execution"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Custom policy for accessing secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${local.name_prefix}-secrets-access"
  description = "Policy for accessing application secrets"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          aws_secretsmanager_secret.db_credentials.arn,
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.google_credentials.arn,
          aws_secretsmanager_secret.whatsapp_credentials.arn,
          aws_secretsmanager_secret.telegram_credentials.arn,
          aws_secretsmanager_secret.app_config.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey"
        ]
        Resource = [
          aws_kms_key.secrets.arn
        ]
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# IAM role for ECS tasks (application runtime)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# Policy for application to access its own secrets
resource "aws_iam_policy" "app_secrets_access" {
  name        = "${local.name_prefix}-app-secrets-access"
  description = "Policy for application to access its secrets at runtime"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.openai_api_key.arn,
          aws_secretsmanager_secret.whatsapp_credentials.arn,
          aws_secretsmanager_secret.telegram_credentials.arn,
          aws_secretsmanager_secret.app_config.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt"
        ]
        Resource = [
          aws_kms_key.secrets.arn
        ]
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "app_secrets_access" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.app_secrets_access.arn
}
