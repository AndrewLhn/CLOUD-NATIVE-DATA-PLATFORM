variable "network_name" {
  description = "Network to attach the container to"
  type        = string
}

variable "minio_root_user" {
  type      = string
  sensitive = true 
}

variable "minio_root_password" {
  type      = string
  sensitive = true
}