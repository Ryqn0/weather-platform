# terraform/main.tf

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_sql_database_instance" "main" {
  name                = "main-instance"
  database_version    = "POSTGRES_16"
  region              = var.region
  deletion_protection = false
  
  settings {
    # Second-generation instance tiers are based on the machine
    # type. See argument reference below.
    tier = "db-f1-micro"
    edition = "ENTERPRISE"
    disk_size = 10          # GB, the minimum
    disk_type = "PD_HDD"    # cheaper than SSD for this use case
    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "home"
        value = "${var.home_ip}/32"
      }
    }
  }
}

resource "google_sql_database" "weather" {
  name     = "weather"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "weather_app" {
  name     = "weather_app"
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

resource "google_storage_bucket" "weather_bucket" {
  name          = "${var.project_id}-raw-data"
  location      = "europe-west1"
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }


}