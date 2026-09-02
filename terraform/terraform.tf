# terraform/terraform.tf

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "8.0.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.9.0"
    }
  }
}