variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for naming all resources"
  type        = string
  default     = "api-reliability-monitor"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}
