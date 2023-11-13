terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }

    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }

    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.3.0"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-east-2"
}

provider "docker"{}

resource "docker_image" "scraping_image" {
  name         = "property_bot"

  build {
    context = "${path.cwd}/../"
  }
}

resource "docker_container" "scraping_container" {
  image = docker_image.scraping_image.image_id
  name  = "property-bot-scraper"
  shm_size=2e9
  
  volumes {
    host_path      = "${path.cwd}/../scraper"
    container_path = "/scraper"
  }
  ports {
    internal = 4444
    external = 4444
  }

  ports {
    internal = 7900
    external = 7900
  }
}
# resource "aws_sqs_queue" "data_queue" {
#   name                       = "property-bot-queue"
#   visibility_timeout_seconds = 30

#   tags = local.tags
# }