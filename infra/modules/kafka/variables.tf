variable "kafka_version" {
  type        = string
  description = "Версия Kafka"
}
variable "network_name" {
  description = "The Docker network name to attach the Kafka broker to"
  type        = string
}