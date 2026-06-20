terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}

resource "docker_image" "kafka_connect" {
  name = "cnfldemos/cp-server-connect-datagen:0.6.2-7.5.0"
}

resource "docker_container" "kafka_connect" {
  name  = "kafka_connect"
  image = docker_image.kafka_connect.image_id

  networks_advanced {
    name = var.network_name
  }

  ports {
    internal = 8083
    external = 8083
  }

  env = [
    "CONNECT_BOOTSTRAP_SERVERS=${var.kafka_bootstrap_servers}",
    "CONNECT_REST_PORT=8083",
    "CONNECT_REST_ADVERTISED_HOST_NAME=kafka_connect",
    "CONNECT_GROUP_ID=quickstart-connect",
    "CONNECT_CONFIG_STORAGE_TOPIC=quickstart-config",
    "CONNECT_OFFSET_STORAGE_TOPIC=quickstart-offsets",
    "CONNECT_STATUS_STORAGE_TOPIC=quickstart-status",
    "CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR=1",
    "CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR=1",
    "CONNECT_STATUS_STORAGE_REPLICATION_FACTOR=1",
    "CONNECT_KEY_CONVERTER=org.apache.kafka.connect.storage.StringConverter",
    "CONNECT_VALUE_CONVERTER=io.confluent.connect.avro.AvroConverter",
    "CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL=http://schema_registry:8081",
    "CONNECT_INTERNAL_KEY_CONVERTER=org.apache.kafka.connect.json.JsonConverter",
    "CONNECT_INTERNAL_VALUE_CONVERTER=org.apache.kafka.connect.json.JsonConverter",
    "CONNECT_PLUGIN_PATH=/usr/share/java,/usr/share/confluent-hub-components"
  ]
}