terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "data_platform_net" {
  name = "data_platform_net"
}

module "storage" {
  source              = "./modules/storage"
  network_name        = docker_network.data_platform_net.name
  minio_version       = var.minio_version
  minio_root_user     = var.minio_root_user
  minio_root_password = var.minio_root_password
}

module "kafka" {
  source        = "./modules/kafka"
  network_name  = docker_network.data_platform_net.name
  kafka_version = var.kafka_version 
}

module "schema_registry" {
  source       = "./modules/schema_registry"
  network_name = docker_network.data_platform_net.name
  depends_on   = [module.kafka]
}

module "kafka_connect" {
  source       = "./modules/kafka_connect"
  network_name = docker_network.data_platform_net.name
  depends_on   = [module.schema_registry, module.kafka]
}


resource "local_file" "s3_sink_rendered" {
  content = templatefile("${path.module}/s3_sink_pageviews.json.tpl", {
    minio_access_key = var.minio_root_user
    minio_secret_key = var.minio_root_password
  })
  filename = "${path.module}/s3_sink_ready.json"
}

resource "null_resource" "deploy_connector" {
  depends_on = [local_file.s3_sink_rendered, module.kafka_connect]

  triggers = {
    config_hash = md5(local_file.s3_sink_rendered.content)
  }

  provisioner "local-exec" {
    command = <<EOT
      curl -X DELETE http://localhost:8083/connectors/s3-sink-pageviews || true
      sleep 2
      curl -i -X POST -H "Content-Type: application/json" --data @${local_file.s3_sink_rendered.filename} http://localhost:8083/connectors
    EOT
  }
}