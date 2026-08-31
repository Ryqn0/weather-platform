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
        value = "82.66.248.188/32"
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