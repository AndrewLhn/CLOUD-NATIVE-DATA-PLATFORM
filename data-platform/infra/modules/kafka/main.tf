resource "docker_image" "kafka" {
  name = "confluentinc/cp-kafka:7.5.0"
}

resource "docker_container" "kafka" {
  name  = "kafka_broker"
  image = docker_image.kafka.image_id
  
  networks_advanced {
    name = var.network_name
  }

  ports {
    internal = 9092
    external = 9092
  }

  env = [
    "KAFKA_NODE_ID=1",
    "KAFKA_PROCESS_ROLES=broker,controller",
    "KAFKA_CONTROLLER_QUORUM_VOTERS=1@kafka_broker:29093",
    "KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:29093",
    "KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092",
    "KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER",
    "KAFKA_CLUSTER_ID=MkU3OEVBNTcwNTJENDM2Qo"
  ]
}