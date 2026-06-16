terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
  api_version = "1.44" 
}

resource "docker_network" "data_platform_net" {
  name = "data_platform_net"
}

module "storage" {
  source              = "./modules/storage"
  network_name        = docker_network.data_platform_net.name
  minio_root_user     = var.minio_root_user
  minio_root_password = var.minio_root_password
}

module "kafka" {
  source       = "./modules/kafka"
  network_name = docker_network.data_platform_net.name
}