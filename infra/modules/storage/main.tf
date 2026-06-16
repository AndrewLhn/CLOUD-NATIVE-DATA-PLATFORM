terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}

resource "docker_image" "minio" {
  name = "minio/minio:${var.minio_version}"
}

resource "docker_container" "minio" {
  name  = "minio_storage"
  image = docker_image.minio.image_id
  

  command = ["server", "/data", "--console-address", ":9001"]
  
  networks_advanced {
    name = var.network_name
  }

  ports {
    internal = 9000
    external = 9000
  }
  ports {
    internal = 9001
    external = 9001
  }

  env = [
    "MINIO_ROOT_USER=${var.minio_root_user}",
    "MINIO_ROOT_PASSWORD=${var.minio_root_password}"
  ]
}

