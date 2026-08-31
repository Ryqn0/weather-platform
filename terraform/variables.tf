# terraform/variables.tf

variable "project_id" {
    description = "GCP project ID"
    type        = string
}

variable "region" {
    description = "GCP region"
    type        = string
}

variable "db_password" {
    description = "Password for the Postgres user"
    type        = string
    sensitive   = true
}

variable "home_ip" {
    description = "IP address of user"
    type        = string
    sensitive   = true
}