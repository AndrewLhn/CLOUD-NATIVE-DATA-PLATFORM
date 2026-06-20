terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}

resource "docker_image" "schema_registry" {
  name = "confluentinc/cp-schema-registry:7.5.0"
}

resource "docker_container" "schema_registry" {
  name  = "schema_registry"
  image = docker_image.schema_registry.image_id

  networks_advanced {
    name = var.network_name
  }

  ports {
    internal = 8081
    external = 8081
  }

  env = [
    "SCHEMA_REGISTRY_HOST_NAME=schema_registry",
    "SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS=${var.kafka_bootstrap_servers}",
    "SCHEMA_REGISTRY_LISTENERS=http://0.0.0.0:8081"
  ]
}