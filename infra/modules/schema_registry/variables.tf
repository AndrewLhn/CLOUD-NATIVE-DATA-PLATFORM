variable "network_name" {
  type        = string
  description = "Имя общей Docker-сети"
}

variable "kafka_bootstrap_servers" {
  type        = string
  default     = "kafka_broker:29093"
  description = "Внутренний адрес Kafka для связи между контейнерами"
}