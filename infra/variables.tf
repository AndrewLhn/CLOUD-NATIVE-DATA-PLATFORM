variable "docker_provider_version" {
  type    = string
  default = "3.0.2"
}

variable "kafka_version" {
  type    = string
  default = "7.5.0"
}

variable "minio_version" {
  type    = string
  default = "latest"
}

variable "minio_root_user" {
  type    = string
}

variable "minio_root_password" {
  type    = string
}