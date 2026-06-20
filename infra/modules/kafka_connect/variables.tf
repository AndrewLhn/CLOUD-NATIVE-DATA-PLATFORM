variable "network_name" {
  type        = string
}

variable "kafka_bootstrap_servers" {
  type        = string
  default     = "kafka_broker:29093"
}
