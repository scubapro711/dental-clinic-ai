# Auto Scaling Configuration
# Automatic scaling for ECS services based on CPU and memory utilization

# Auto Scaling Target for Gateway Service
resource "aws_appautoscaling_target" "gateway" {
  count = var.enable_auto_scaling ? 1 : 0
  
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.gateway.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-gateway-autoscaling-target"
  })
}

# Auto Scaling Target for AI Agents Service
resource "aws_appautoscaling_target" "ai_agents" {
  count = var.enable_auto_scaling ? 1 : 0
  
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.ai_agents.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-ai-agents-autoscaling-target"
  })
}

# CPU-based Auto Scaling Policy for Gateway
resource "aws_appautoscaling_policy" "gateway_cpu" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-gateway-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.gateway[0].resource_id
  scalable_dimension = aws_appautoscaling_target.gateway[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.gateway[0].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    
    target_value       = var.target_cpu_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Memory-based Auto Scaling Policy for Gateway
resource "aws_appautoscaling_policy" "gateway_memory" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-gateway-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.gateway[0].resource_id
  scalable_dimension = aws_appautoscaling_target.gateway[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.gateway[0].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    
    target_value       = var.target_memory_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# CPU-based Auto Scaling Policy for AI Agents
resource "aws_appautoscaling_policy" "ai_agents_cpu" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-ai-agents-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ai_agents[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ai_agents[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ai_agents[0].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    
    target_value       = var.target_cpu_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Memory-based Auto Scaling Policy for AI Agents
resource "aws_appautoscaling_policy" "ai_agents_memory" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-ai-agents-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ai_agents[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ai_agents[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ai_agents[0].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    
    target_value       = var.target_memory_utilization
    scale_in_cooldown  = 300
    scale_out_cooldown = 300
  }
}

# Custom CloudWatch Metrics for Auto Scaling
resource "aws_cloudwatch_metric_alarm" "gateway_high_cpu" {
  count = var.enable_auto_scaling ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-gateway-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS Gateway service CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ServiceName = aws_ecs_service.gateway.name
    ClusterName = aws_ecs_cluster.main.name
  }
  
  tags = local.common_tags
}

resource "aws_cloudwatch_metric_alarm" "ai_agents_high_cpu" {
  count = var.enable_auto_scaling ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-ai-agents-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "This metric monitors ECS AI Agents service CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ServiceName = aws_ecs_service.ai_agents.name
    ClusterName = aws_ecs_cluster.main.name
  }
  
  tags = local.common_tags
}

# Queue-based Auto Scaling for AI Agents (based on Redis queue length)
resource "aws_cloudwatch_metric_alarm" "redis_queue_length" {
  count = var.enable_auto_scaling ? 1 : 0
  
  alarm_name          = "${local.name_prefix}-redis-queue-length"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CurrItems"
  namespace           = "AWS/ElastiCache"
  period              = "60"
  statistic           = "Average"
  threshold           = "10"
  alarm_description   = "This metric monitors Redis queue length for AI processing"
  alarm_actions       = [aws_appautoscaling_policy.ai_agents_cpu[0].arn]
  
  dimensions = {
    CacheClusterId = aws_elasticache_cluster.redis.cluster_id
  }
  
  tags = local.common_tags
}

# Step Scaling Policy for High Queue Length
resource "aws_appautoscaling_policy" "ai_agents_queue_scaling" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-ai-agents-queue-scaling"
  policy_type        = "StepScaling"
  resource_id        = aws_appautoscaling_target.ai_agents[0].resource_id
  scalable_dimension = aws_appautoscaling_target.ai_agents[0].scalable_dimension
  service_namespace  = aws_appautoscaling_target.ai_agents[0].service_namespace
  
  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown               = 300
    metric_aggregation_type = "Average"
    
    step_adjustment {
      metric_interval_lower_bound = 0
      metric_interval_upper_bound = 20
      scaling_adjustment          = 1
    }
    
    step_adjustment {
      metric_interval_lower_bound = 20
      metric_interval_upper_bound = 50
      scaling_adjustment          = 2
    }
    
    step_adjustment {
      metric_interval_lower_bound = 50
      scaling_adjustment          = 3
    }
  }
}

# Scheduled Scaling for Predictable Load Patterns
resource "aws_appautoscaling_scheduled_action" "scale_up_morning" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-scale-up-morning"
  service_namespace  = aws_appautoscaling_target.gateway[0].service_namespace
  resource_id        = aws_appautoscaling_target.gateway[0].resource_id
  scalable_dimension = aws_appautoscaling_target.gateway[0].scalable_dimension
  
  schedule = "cron(0 8 * * MON-FRI)"
  
  scalable_target_action {
    min_capacity = var.min_capacity + 1
    max_capacity = var.max_capacity
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_down_evening" {
  count = var.enable_auto_scaling ? 1 : 0
  
  name               = "${local.name_prefix}-scale-down-evening"
  service_namespace  = aws_appautoscaling_target.gateway[0].service_namespace
  resource_id        = aws_appautoscaling_target.gateway[0].resource_id
  scalable_dimension = aws_appautoscaling_target.gateway[0].scalable_dimension
  
  schedule = "cron(0 20 * * MON-FRI)"
  
  scalable_target_action {
    min_capacity = var.min_capacity
    max_capacity = var.max_capacity
  }
}
